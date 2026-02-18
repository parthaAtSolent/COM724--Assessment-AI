import streamlit as st
import pandas as pd


def render_today_section(data):
    """Render Today section in card format"""
    if data is None or data.empty:
        return

    # Get today's and yesterday's data
    today_data = data.iloc[-1]
    yesterday_data = data.iloc[-2] if len(data) > 1 else today_data

    # Calculate changes
    pre_market_change = today_data['Open'] - yesterday_data['Close']
    pre_market_pct = (pre_market_change / yesterday_data['Close']) * 100

    # Format dates
    yesterday_time = yesterday_data.name.strftime('%B %d, %I:%M%p')
    today_time = today_data.name.strftime('%B %d, %I:%M%p')

    # Determine color for change
    change_color = '#27ae60' if pre_market_change >= 0 else '#c0392b'

    st.html(
        f"""
        <div class="card today-card style="height:100%;">
            <div class="today-title">TODAY</div>
            
            <div class="today-grid">
                <div class="today-item">
                    <div class="today-label">Pre-market</div>
                    <div class="today-value">${today_data['Open']:,.2f}</div>
                    <div class="today-change" style="color: {change_color}">
                        {pre_market_change:+.2f} ({pre_market_pct:+.2f}%)
                    </div>
                </div>
                
                <div class="today-item">
                    <div class="today-label">Previous Close</div>
                    <div class="today-value">${yesterday_data['Close']:,.2f}</div>
                    <div class="today-time">{yesterday_time}</div>
                </div>
                
                <div class="today-item">
                    <div class="today-label">Open</div>
                    <div class="today-value">${today_data['Open']:,.2f}</div>
                    <div class="today-time">{today_time}</div>
                </div>
            </div>
        </div>
        """
    )
