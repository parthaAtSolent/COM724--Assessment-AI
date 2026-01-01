import streamlit as st
from data.data_loader import load_data, CRYPTOS
from models.prophet_forecast import prophet_forecast
from models.arima_forecast import arima_forecast
from models.lstm_forecast import lstm_forecast
from models.random_forest_forecast import random_forest_forecast
from utils.logo import load_custom_css, display_logo


# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------
st.set_page_config(
    page_title="Solent Intelligence - Crypto Price Forecasting",
    page_icon="📈",
    layout="wide"
)

# ---------------------------------------------------
# Load Custom CSS & Display Logo
# ---------------------------------------------------
load_custom_css("styles/style.css")
display_logo("assets/logo2.png")

# ---------------------------------------------------
# Main Application
# ---------------------------------------------------


def main():
    st.title('Cryptocurrency Price Forecasting Application')

    # Sidebar configuration
    st.sidebar.title("Configuration")
    selected_models = st.sidebar.multiselect(
        "Select forecasting models:",
        ["Prophet", "ARIMA", "LSTM", "Random Forest"],
        default=["ARIMA", "Prophet"]
    )

    selected_name = st.selectbox(
        'Select cryptocurrency for prediction',
        list(CRYPTOS.values())
    )

    # Get the crypto symbol
    selected_crypto = [k for k, v in CRYPTOS.items() if v == selected_name][0]

    # Forecast duration
    n_years = st.slider('Years of prediction:', 1, 5)
    period = n_years * 365

    # Load data
    data = load_data(selected_crypto)

    if data is not None:
        # Show data
        st.subheader('Raw Data')
        st.write(data.tail())

        # Run selected models
        if "Prophet" in selected_models:
            prophet_forecast(data, period, n_years, selected_name)

        if "ARIMA" in selected_models:
            arima_forecast(data, period, n_years, selected_name)

        if "LSTM" in selected_models:
            lstm_forecast(data, period, n_years, selected_name)

        if "Random Forest" in selected_models:
            random_forest_forecast(data, period, n_years, selected_name)
    else:
        st.error("Failed to load data. Please try again.")


if __name__ == "__main__":
    main()
