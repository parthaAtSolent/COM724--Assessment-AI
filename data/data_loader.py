import os
import streamlit as st
import yfinance as yf
import pandas as pd
from config.settings import START_DATE, TODAY
from utils.preprocessing import preprocessing


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

        btc_preprocessed = preprocessing(data)

        # print(btc_preprocessed.head())

        return btc_preprocessed

    except Exception as e:
        st.error(f"Error loading data for {ticker}: {str(e)}")
        return None
