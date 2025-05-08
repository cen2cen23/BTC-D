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

    # Memeriksa apakah data harga ada dalam respons
    if 'prices' not in btc_data:
        print(f"Error: Tidak ada data harga Bitcoin ditemukan.\nRespons: {btc_data}")
        raise ValueError("Data harga Bitcoin tidak ditemukan dalam respons API")

    if 'prices' not in eth_data:
        print(f"Error: Tidak ada data harga Ethereum ditemukan.\nRespons: {eth_data}")
        raise ValueError("Data harga Ethereum tidak ditemukan dalam respons API")
    
    # Mengambil harga dan timestamp
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

# Mengambil data
try:
    df = get_data()
    print("Data berhasil diambil dan diproses.")
except ValueError as e:
    print(f"Error: {e}")
    df = pd.DataFrame()  # Menghasilkan DataFrame kosong jika terjadi error

# Memeriksa apakah data diambil dengan benar
if df.empty:
    print("Tidak ada data yang berhasil diambil.")
else:
    print("DataFrame head:")
    print(df.head())  # Menampilkan 5 baris pertama untuk pemeriksaan

# Menampilkan DataFrame di Streamlit jika ada data
if not df.empty:
    st.write(df)
    
    # Menampilkan grafik dominasi Bitcoin
    plt.figure(figsize=(10, 6))
    plt.plot(df['timestamp'], df['btc_dominance'], label='Bitcoin Dominance', color='blue')
    plt.xlabel('Tanggal')
    plt.ylabel('Dominasi Bitcoin (%)')
    plt.title('Prediksi Dominasi Bitcoin Terhadap Altcoin')
    plt.xticks(rotation=45)
    plt.legend()
    st.pyplot(plt)
