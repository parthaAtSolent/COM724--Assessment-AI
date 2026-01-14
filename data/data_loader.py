import os
import streamlit as st
import yfinance as yf
import pandas as pd
from config.settings import START_DATE, TODAY
from utils.preprocessing import preprocessing

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
    """Load cryptocurrency data from Yahoo Finance and save as CSV"""
    try:
        # Download data
        data = yf.download(ticker, START_DATE, TODAY)
        data.reset_index(inplace=True)
        print("Testing data download...")

        # Flatten column names if multi-indexed
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]

        # -------------------------------
        # Create directory: data/<ticker>/
        # -------------------------------
        base_dir = "data"
        ticker_dir = os.path.join(base_dir, ticker)

        os.makedirs(ticker_dir, exist_ok=True)

        # -------------------------------
        # CSV file name and path
        # -------------------------------
        file_name = f"{ticker}_from_{START_DATE}_till_{TODAY}.csv"
        file_path = os.path.join(ticker_dir, file_name)

        # -------------------------------
        # Save to CSV
        # -------------------------------
        data.to_csv(file_path, index=False)

        print(f"Data saved to: {file_path}")

        # return data

        # This will automatically find and load the CSV file
        btc_preprocessed = preprocessing(data)

        # print(btc_preprocessed.head())

        return btc_preprocessed

    except Exception as e:
        st.error(f"Error loading data for {ticker}: {str(e)}")
        return None
