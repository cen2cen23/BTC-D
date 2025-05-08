
import streamlit as st
import requests
import matplotlib.pyplot as plt

st.set_page_config(page_title="Bitcoin Dominance Tracker", layout="centered")

st.title("📊 Bitcoin Dominance dari CoinGecko")

@st.cache_data(ttl=600)
def fetch_btc_dominance():
    url = "https://api.coingecko.com/api/v3/global"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "btc_dominance": data['data']['market_cap_percentage']['btc'],
            "eth_dominance": data['data']['market_cap_percentage']['eth'],
            "total_market_cap": data['data']['total_market_cap']['usd'],
            "active_cryptos": data['data']['active_cryptocurrencies']
        }
    else:
        st.error("Gagal mengambil data dari CoinGecko.")
        return None

data = fetch_btc_dominance()

if data:
    st.metric("Dominasi Bitcoin", f"{data['btc_dominance']:.2f}%")
    st.metric("Dominasi Ethereum", f"{data['eth_dominance']:.2f}%")
    st.metric("Total Market Cap", f"US${data['total_market_cap']:,.0f}")
    st.metric("Jumlah Aset Kripto Aktif", data['active_cryptos'])

    # Pie Chart
    labels = ['Bitcoin', 'Ethereum', 'Lainnya']
    sizes = [
        data['btc_dominance'],
        data['eth_dominance'],
        100 - data['btc_dominance'] - data['eth_dominance']
    ]
    colors = ['#f7931a', '#3c3c3d', '#aaaaaa']

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    ax.axis('equal')
    st.pyplot(fig)
