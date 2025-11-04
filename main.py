import streamlit as st
from data.data_loader import load_data, CRYPTOS
from models.prophet_forecast import prophet_forecast
from models.arima_forecast import arima_forecast
from models.lstm_forecast import lstm_forecast
from models.random_forest_forecast import random_forest_forecast
from utils.config import START_DATE

# Page configuration
st.set_page_config(
    page_title="Cryptocurrency Forecast App",
    page_icon="📈",
    layout="wide"
)


def main():
    st.title('Cryptocurrency Forecast App')

    # Sidebar for model selection
    st.sidebar.title("Configuration")
    selected_models = st.sidebar.multiselect(
        "Select forecasting models:",
        ["Prophet", "ARIMA", "LSTM", "Random Forest"],
        default=["LSTM"]
    )

    # Main content
    selected_name = st.selectbox(
        'Select cryptocurrency for prediction',
        list(CRYPTOS.values())
    )

    # Get the symbol corresponding to the selected name
    selected_crypto = [k for k, v in CRYPTOS.items() if v == selected_name][0]

    n_years = st.slider('Years of prediction:', 1, 4)
    period = n_years * 365

    # Load data
    data = load_data(selected_crypto)

    if data is not None:
        # Display raw data and plot
        st.subheader('Raw Data')
        st.write(data.tail())

        # Model forecasts
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
