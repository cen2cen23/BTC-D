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

    # Memeriksa respons API dan mencetak data
    print("Data BTC:", btc_data)  # Cek data BTC
    print("Data ETH:", eth_data)  # Cek data ETH

    # Memeriksa apakah data harga ada dalam respons
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
    print("DataFrame head:", df.head())  # Menampilkan 5 baris pertama

