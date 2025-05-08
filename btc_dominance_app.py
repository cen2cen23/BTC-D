import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import streamlit as st

# Fungsi untuk mengambil data dari CoinGecko
def get_data():
    btc_url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30"
    eth_url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=30"
    
    # Mengambil data harga Bitcoin dan Ethereum
    btc_data = requests.get(btc_url).json()
    eth_data = requests.get(eth_url).json()

    # Periksa apakah data berhasil diterima
    print("Data BTC:", btc_data)  # Cek data BTC
    print("Data ETH:", eth_data)  # Cek data ETH

    if 'prices' not in btc_data or 'prices' not in eth_data:
        raise ValueError("Data harga tidak ditemukan dalam respons API")

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

# Memeriksa apakah data diambil dengan benar
print("DataFrame head:", df.head())  # Menampilkan 5 baris pertama

# Menghitung indikator teknikal
df['rsi'] = calculate_rsi(df['btc_dominance'])
df['macd'], df['macd_signal'], df['macd_hist'] = calculate_macd(df['btc_dominance'])

# Menghitung moving averages
df['ma_7'] = df['btc_dominance'].rolling(window=7).mean()
df['ma_30'] = df['btc_dominance'].rolling(window=30).mean()

# Analisis crossover MA
crossover_signal = np.where(df['ma_7'] < df['ma_30'], 1, 0)

# Menampilkan grafik dengan Streamlit
st.title("Analisis Dominasi Bitcoin")

# Menampilkan grafik
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df['timestamp'], df['btc_dominance'], label="Dominasi Bitcoin", color='b')
ax.plot(df['timestamp'], df['ma_7'], label="MA 7 hari", color='g', linestyle='--')
ax.plot(df['timestamp'], df['ma_30'], label="MA 30 hari", color='r', linestyle='--')
ax.set_title("Analisis Moving Average pada Dominasi Bitcoin")
ax.set_xlabel("Tanggal")
ax.set_ylabel("Dominasi Bitcoin (%)")
ax.legend()
ax.set_xticklabels(df['timestamp'], rotation=45)
plt.tight_layout()

# Menampilkan grafik di Streamlit
st.pyplot(fig)

# Menampilkan analisis teks berdasarkan indikator teknikal
def analyze_indicators():
    analysis = []
    
    # Nilai Dominasi Bitcoin terkini
    current_dominance = df['btc_dominance'].iloc[-1]
    analysis.append(f"Dominasi Bitcoin terkini: {current_dominance:.2f}%")
    
    # Analisis RSI
    current_rsi = df['rsi'].iloc[-1]
    if current_rsi > 70:
        analysis.append(f"RSI: {current_rsi:.2f} - Dominasi Bitcoin overbought, potensi penurunan.")
    elif current_rsi < 30:
        analysis.append(f"RSI: {current_rsi:.2f} - Dominasi Bitcoin oversold, potensi kenaikan.")
    else:
        analysis.append(f"RSI: {current_rsi:.2f} - Dominasi Bitcoin berada dalam zona netral.")
    
    # Analisis MACD
    current_macd_hist = df['macd_hist'].iloc[-1]
    if current_macd_hist > 0:
        analysis.append(f"MACD Histogram: {current_macd_hist:.2f} - Tren bullish pada dominasi Bitcoin.")
    elif current_macd_hist < 0:
        analysis.append(f"MACD Histogram: {current_macd_hist:.2f} - Tren bearish pada dominasi Bitcoin.")
    else:
        analysis.append(f"MACD Histogram: {current_macd_hist:.2f} - Tidak ada tren yang jelas.")
    
    # Analisis Crossover MA
    if crossover_signal[-1] == 1:
        analysis.append(f"Crossover MA: MA 7 hari lebih rendah dari MA 30 hari, kemungkinan penurunan.")
    else:
        analysis.append(f"Crossover MA: MA 7 hari lebih tinggi dari MA 30 hari, menunjukkan tren naik.")
    
    # Gabungkan semua analisis
    return "\n".join(analysis)

# Tampilkan analisis teks di Streamlit
st.subheader("Analisis Dominasi Bitcoin")
st.text(analyze_indicators())
