import streamlit as st
import yfinance as yf
import pandas as pd
from config.settings import START_DATE, TODAY

CRYPTOS = {
    'BTC-USD': 'Bitcoin',
    'ETH-USD': 'Ethereum',
    'BNB-USD': 'Binance Coin',
    'XRP-USD': 'Ripple',
    'SOL-USD': 'Solana',
    'ADA-USD': 'Cardano',
    'DOGE-USD': 'Dogecoin',
    'DOT-USD': 'Polkadot',
    'AVAX-USD': 'Avalanche',
    'MATIC-USD': 'Polygon',
    'SHIB-USD': 'Shiba Inu',
    'LTC-USD': 'Litecoin',
    'TRX-USD': 'TRON',
    'BCH-USD': 'Bitcoin Cash',
    'ATOM-USD': 'Cosmos',
    'LINK-USD': 'Chainlink',
    'XLM-USD': 'Stellar',
    'UNI-USD': 'Uniswap',
    'XMR-USD': 'Monero',
    'ETC-USD': 'Ethereum Classic',
    'NEAR-USD': 'NEAR Protocol',
    'VET-USD': 'VeChain',
    'ICP-USD': 'Internet Computer',
    'FIL-USD': 'Filecoin',
    'EOS-USD': 'EOS',
    'APT-USD': 'Aptos',
    'SAND-USD': 'The Sandbox',
    'AAVE-USD': 'Aave',
    'MANA-USD': 'Decentraland',
    'THETA-USD': 'Theta Network',
    'EGLD-USD': 'MultiversX (Elrond)'
}


@st.cache_data(show_spinner=False)
def load_data(ticker):
    """Load cryptocurrency data from Yahoo Finance"""
    try:
        data = yf.download(ticker, START_DATE, TODAY)
        data.reset_index(inplace=True)

        # Flatten column names if they are multi-indexed
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]

        # print(data.head())
        return data
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {str(e)}")
        return None
