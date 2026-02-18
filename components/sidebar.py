import streamlit as st
from data.data_loader import CRYPTOS


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
        default=["ARIMA"]
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

    # Advanced options (optional)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 Advanced Options")
    show_raw_data = st.sidebar.checkbox("Show raw data", value=True)
    confidence_interval = st.sidebar.slider(
        "Confidence interval (%)",
        min_value=80,
        max_value=99,
        value=95
    )

    return {
        "selected_models": selected_models,
        "selected_crypto": selected_crypto,
        "selected_name": selected_name,
        "period": period,
        "n_years": n_years,
        "show_raw_data": show_raw_data,
        "confidence_interval": confidence_interval / 100  # Convert to decimal
    }
