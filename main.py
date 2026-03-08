# 🔹 Forecasting = numeric prediction + time
# 🔹 Prediction = any informed statement(/category, /probability, /numeric value) about an outcome

import streamlit as st
from data.data_loader import load_data
from utils.logo import load_custom_css, display_logo
from components.sidebar import render_sidebar
from components.header import render_header
from components.info import render_info_section
from components.chart_container import render_chart_container
from components.today_section import render_today_section
from components.details_grid import render_details_grid
from components.trade_section import render_trade_section
from components.forecast import execute_forecasts


# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------
st.set_page_config(
    page_title="Solent Intelligence - Crypto Price Forecasting",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
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
    """Main application function"""

    # Render sidebar and get configuration
    config = render_sidebar()

    # Load data based on selected cryptocurrency
    data = load_data(config["selected_crypto"])

    # Main content area
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)

    if data is not None and not data.empty:
        # 1. Header with name, symbol, and price
        render_header(data, config["selected_name"], config["selected_crypto"])

        # 2. Horizontal layout for Info and Today sections
        st.markdown("<div class='info-today-wrapper'>", unsafe_allow_html=True)

        # Create two columns for the horizontal layout
        col1, col2 = st.columns(2)

        with col1:
            # Info section card (left)
            render_info_section(data, config["selected_crypto"])

        with col2:
            # Today section card (right)
            render_today_section(data)

        st.markdown("</div>", unsafe_allow_html=True)

        # 3. Main chart with period selector
        render_chart_container(data)

        # 6. Forecasts section
        # st.markdown("<div class='forecast-section'>", unsafe_allow_html=True)

        execute_forecasts(
            data=data,
            period=config["period"],
            n_years=config["n_years"],
            selected_name=config["selected_name"],
            selected_models=config["selected_models"],
            confidence_interval=config["confidence_interval"]
        )
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.error("🚨 Failed to load cryptocurrency data.")
        st.info("""
        Possible reasons:
        1. Network connection issue
        2. Invalid cryptocurrency symbol
        3. Data source temporarily unavailable
        
        Please try:
        - Checking your internet connection
        - Selecting a different cryptocurrency
        - Refreshing the page
        """)

    # Footer
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="footer">
        <p>Solent Intelligence Crypto Forecasting Platform | Data for informational purposes only</p>
        <p>Past performance is not indicative of future results</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
