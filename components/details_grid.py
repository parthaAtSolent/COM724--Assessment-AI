import streamlit as st
import pandas as pd
import numpy as np


def render_details_grid(data):
    """Render details in grid format like financial platforms"""
    st.markdown("## Details")

    if data is None or data.empty:
        return

    # Calculate metrics
    current_price = data['Close'].iloc[-1]

    # Day's Range
    day_low = data['Low'].iloc[-1]
    day_high = data['High'].iloc[-1]

    # 52 Week Range (using 1 year if available)
    year_data = data.last('365D') if len(data) > 365 else data
    week52_low = year_data['Low'].min()
    week52_high = year_data['High'].max()

    # Volume metrics
    volume = data['Volume'].iloc[-1]
    avg_volume = data['Volume'].tail(30).mean()

    # Placeholder values for other metrics (would need real API data)
    market_cap = current_price * 1e9  # Placeholder
    beta = 1.21
    pe_ratio = 29.25
    eps = 4.45
    forward_div = 0.88
    ex_div_date = "2021/05/07"

    # Create details grid container
    st.markdown('<div class="details-grid">', unsafe_allow_html=True)

    # Create two columns for the grid
    col1, col2 = st.columns(2)

    with col1:
        _detail_item("Day's Range", f"{day_low:.2f} - {day_high:.2f}")
        _detail_item("52 Week Range", f"{week52_low:.2f} - {week52_high:.2f}")
        _detail_item("Volume", f"{volume:,.0f}")
        _detail_item("Avg. Volume", f"{avg_volume:,.0f}")
        _detail_item("Market Cap", f"{market_cap/1e12:.3f}T")

    with col2:
        _detail_item("Beta (5Y Monthly)", f"{beta:.2f}")
        _detail_item("PE Ratio (TTM)", f"{pe_ratio:.2f}")
        _detail_item("EPS (TTM)", f"{eps:.2f}")
        _detail_item("Forward Dividend", f"{forward_div:.2f}")
        _detail_item("Ex-Dividend Date", ex_div_date)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")


def _detail_item(title, value):
    """Render a detail item in financial format"""
    st.markdown(f"""
    <div class="detail-item">
        <div class="detail-label">{title}</div>
        <div class="detail-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)
