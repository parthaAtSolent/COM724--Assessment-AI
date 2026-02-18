import streamlit as st
import pandas as pd


def render_trade_section(data):
    """Render Buy/Sell table and buttons like financial platforms"""
    if data is None or data.empty:
        return

    current_price = data['Close'].iloc[-1]

    # Create trading section
    st.markdown('<div class="trading-section">', unsafe_allow_html=True)
    st.markdown("### Trading")

    # Trading table
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(f"""
        <table class="trading-table">
            <thead>
                <tr>
                    <th class="buy-header">Buy</th>
                    <th class="sell-header">Sell</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="buy-price">${current_price*0.995:,.2f}</td>
                    <td class="sell-price">${current_price*1.005:,.2f}</td>
                </tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)

    # Trading buttons
    st.markdown("<br>", unsafe_allow_html=True)

    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])

    with btn_col2:
        col_left, col_right = st.columns(2)

        with col_left:
            if st.button("🟢 BUY", use_container_width=True, type="primary"):
                st.success(f"Buy order placed at ${current_price:,.2f}")

        with col_right:
            if st.button("🔴 SELL", use_container_width=True, type="secondary"):
                st.error(f"Sell order placed at ${current_price:,.2f}")

    st.markdown('</div>', unsafe_allow_html=True)
