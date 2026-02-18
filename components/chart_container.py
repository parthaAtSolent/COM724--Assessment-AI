import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def render_chart_container(data):
    """Render chart with period selector exactly like financial interfaces"""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### Chart")

    # Period selector buttons
    periods = ["1d", "5d", "2w", "1m", "6m", "1y", "5y", "max"]
    cols = st.columns(len(periods))

    selected_period = "1y"  # Default

    for i, period in enumerate(periods):
        with cols[i]:
            if st.button(period.upper(), key=f"chart_{period}", use_container_width=True):
                selected_period = period

    # Filter data based on period
    filtered_data = _filter_data_by_period(data, selected_period)

    # Create chart
    fig = go.Figure()

    # Add candlestick
    fig.add_trace(go.Candlestick(
        x=filtered_data.index,
        open=filtered_data['Open'],
        high=filtered_data['High'],
        low=filtered_data['Low'],
        close=filtered_data['Close'],
        name="Price",
        increasing_line_color='#27ae60',
        decreasing_line_color='#c0392b'
    ))

    # Clean financial layout
    fig.update_layout(
        height=450,
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            color='#666666'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.1)',
            side='right',
            color='#666666'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=20, r=20, t=30, b=20)
    )

    fig.update_xaxes(showticklabels=False)

    st.plotly_chart(fig, use_container_width=True)

    # Chart annotations (financial style)
    if len(filtered_data) > 0:
        last_row = filtered_data.iloc[-1]
        st.markdown("""
        <div class="chart-annotations">
            <div>
                <div><strong>Open:</strong> ${:,.2f}</div>
                <div><strong>High:</strong> ${:,.2f}</div>
                <div><strong>Low:</strong> ${:,.2f}</div>
                <div><strong>Close:</strong> ${:,.2f}</div>
                <div><strong>Change:</strong> {:.2f}%</div>
            </div>
        </div>
        """.format(
            last_row['Open'], last_row['High'], last_row['Low'],
            last_row['Close'], ((last_row['Close'] -
                                last_row['Open']) / last_row['Open'] * 100)
        ), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    return selected_period


def _filter_data_by_period(data, period):
    """Filter data based on selected period"""
    end_date = data.index[-1]

    if period == "1d":
        start_date = end_date - pd.Timedelta(days=1)
    elif period == "5d":
        start_date = end_date - pd.Timedelta(days=5)
    elif period == "2w":
        start_date = end_date - pd.Timedelta(weeks=2)
    elif period == "1m":
        start_date = end_date - pd.Timedelta(days=30)
    elif period == "6m":
        start_date = end_date - pd.Timedelta(days=180)
    elif period == "1y":
        start_date = end_date - pd.Timedelta(days=365)
    elif period == "5y":
        start_date = end_date - pd.Timedelta(days=5*365)
    else:  # max
        start_date = data.index[0]

    return data[data.index >= start_date]
