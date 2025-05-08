import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Fungsi untuk mengambil data dari CoinGecko
def get_data():
    btc_url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30"
    eth_url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=30"
    
    # Mengambil data harga Bitcoin dan Ethereum
    btc_data = requests.get(btc_url).json()
    eth_data = requests.get(eth_url).json()
    
    # Data harga dan volume BTC dan ETH
    btc_prices = np.array([x[1] for x in btc_data['prices']])
    eth_prices = np.array([x[1] for x in eth_data['prices']])
    timestamps = [datetime.utcfromtimestamp(x[0] / 1000) for x in btc_data['prices']]
    
    # Membuat DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'btc_price': btc_prices,
        'eth_price': eth_prices
    })
    
    # Menghitung dominasi Bitcoin
    df['btc_dominance'] = (df['btc_price'] / (df['btc_price'] + df['eth_price'])) * 100
    
    return df

# Fungsi untuk menghitung indikator RSI
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

# Fungsi untuk menghitung MACD
def calculate_macd(data, fast=12, slow=26, signal=9):
    macd = data.ewm(span=fast, adjust=False).mean() - data.ewm(span=slow, adjust=False).mean()
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal
    return macd, macd_signal, macd_hist

# Mengambil data
df = get_data()

# Menghitung indikator teknikal
df['rsi'] = calculate_rsi(df['btc_dominance'])
df['macd'], df['macd_signal'], df['macd_hist'] = calculate_macd(df['btc_dominance'])

# Menghitung moving averages
df['ma_7'] = df['btc_dominance'].rolling(window=7).mean()
df['ma_30'] = df['btc_dominance'].rolling(window=30).mean()

# Analisis crossover MA
crossover_signal = np.where(df['ma_7'] < df['ma_30'], 1, 0)

# Menampilkan grafik
plt.figure(figsize=(10, 5))
plt.plot(df['timestamp'], df['btc_dominance'], label="Dominasi Bitcoin", color='b')
plt.plot(df['timestamp'], df['ma_7'], label="MA 7 hari", color='g', linestyle='--')
plt.plot(df['timestamp'], df['ma_30'], label="MA 30 hari", color='r', linestyle='--')
plt.title("Analisis Moving Average pada Dominasi Bitcoin")
plt.xlabel("Tanggal")
plt.ylabel("Dominasi Bitcoin (%)")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

# Menyimpan grafik crossover
plt.savefig("btc_dominance_ma_crossover.png")
plt.show()

# Menampilkan analisis teks berdasarkan indikator teknikal
def analyze_indicators():
    analysis = []
    
    # Analisis RSI
    if df['rsi'].iloc[-1] > 70:
        analysis.append("RSI menunjukkan bahwa dominasi Bitcoin sedang overbought, yang bisa berarti penurunan di masa depan.")
    elif df['rsi'].iloc[-1] < 30:
        analysis.append("RSI menunjukkan bahwa dominasi Bitcoin sedang oversold, yang bisa berarti potensi kenaikan.")
    else:
        analysis.append("RSI berada dalam zona netral, menandakan dominasi Bitcoin bisa bergerak dalam rentang yang lebih stabil.")
    
    # Analisis MACD
    if df['macd_hist'].iloc[-1] > 0:
        analysis.append("MACD menunjukkan tren bullish pada dominasi Bitcoin.")
    elif df['macd_hist'].iloc[-1] < 0:
        analysis.append("MACD menunjukkan tren bearish pada dominasi Bitcoin.")
    else:
        analysis.append("MACD berada dalam kondisi netral, dengan dominasi Bitcoin tidak menunjukkan tren yang jelas.")
    
    # Analisis Crossover MA
    if crossover_signal[-1] == 1:
        analysis.append("Sinyal crossover MA menunjukkan kemungkinan penurunan dominasi Bitcoin.")
    else:
        analysis.append("Dominasi Bitcoin masih menunjukkan kekuatan dengan crossover MA yang mendukung tren naik.")
    
    # Gabungkan semua analisis
    return "\n".join(analysis)

# Tampilkan analisis teks
print("Analisis Dominasi Bitcoin:")
print(analyze_indicators())
