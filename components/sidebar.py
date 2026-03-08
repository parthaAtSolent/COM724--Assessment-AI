import streamlit as st
from config.settings import CRYPTOS


def render_sidebar():
    """
    Render the sidebar with configuration options
    Returns dictionary with user selections
    """
    st.sidebar.title("⚙️ Configuration")

    # Model selection
    st.sidebar.markdown("### 📊 Forecasting Models")
    selected_models = st.sidebar.multiselect(
        "Select models to compare:",
        ["Prophet", "ARIMA", "LSTM", "Random Forest"],
        default=["Prophet"]
    )

    # Cryptocurrency selection
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💰 Cryptocurrency")
    selected_name = st.sidebar.selectbox(
        'Choose a cryptocurrency:',
        list(CRYPTOS.values())
    )

    # Get the crypto symbol
    selected_crypto = [k for k, v in CRYPTOS.items() if v == selected_name][0]

    # Forecast duration
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📅 Forecast Horizon")
    n_years = st.sidebar.slider(
        'Years of prediction:',
        min_value=1,
        max_value=5,
        value=2,
        help="Select how many years into the future to forecast"
    )

    period = n_years * 365

    # Return configuration without advanced options
    return {
        "selected_models": selected_models,
        "selected_crypto": selected_crypto,
        "selected_name": selected_name,
        "period": period,
        "n_years": n_years,
        "show_raw_data": True,  # Set to default value
        "confidence_interval": 0.95  # Set to default value (95%)
    }
