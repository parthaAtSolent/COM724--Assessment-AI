import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def render_chart_container(data):
    """Render chart with period selector exactly like financial interfaces"""

    # Spacer (equivalent to top:2.2rem)
    st.markdown("<div style='height:2.5rem'></div>", unsafe_allow_html=True)

    st.markdown("## Chart")

    periods = ["1d", "5d", "2w", "1m", "6m", "1y", "5y", "max"]

    col1, col2, col3, col4 = st.columns(4)

    selected_period = "1y"

    with col1:
        if st.button(periods[0].upper(), key=f"chart_{periods[0]}", use_container_width=True):
            selected_period = periods[0]

    with col2:
        if st.button(periods[1].upper(), key=f"chart_{periods[1]}", use_container_width=True):
            selected_period = periods[1]

    with col3:
        if st.button(periods[2].upper(), key=f"chart_{periods[2]}", use_container_width=True):
            selected_period = periods[2]

    with col4:
        if st.button(periods[3].upper(), key=f"chart_{periods[3]}", use_container_width=True):
            selected_period = periods[3]

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        if st.button(periods[4].upper(), key=f"chart_{periods[4]}", use_container_width=True):
            selected_period = periods[4]

    with col6:
        if st.button(periods[5].upper(), key=f"chart_{periods[5]}", use_container_width=True):
            selected_period = periods[5]

    with col7:
        if st.button(periods[6].upper(), key=f"chart_{periods[6]}", use_container_width=True):
            selected_period = periods[6]

    with col8:
        if st.button(periods[7].upper(), key=f"chart_{periods[7]}", use_container_width=True):
            selected_period = periods[7]

    filtered_data = _filter_data_by_period(data, selected_period)

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=filtered_data.index,
        open=filtered_data['Open'],
        high=filtered_data['High'],
        low=filtered_data['Low'],
        close=filtered_data['Close'],
        name="Price",
        increasing_line_color='#27ae60',
        decreasing_line_color='#c0392b',
        line=dict(width=0.8),
        whiskerwidth=0.8,
    ))

    fig.update_layout(
        height=300,
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            color='#666666',
            rangeslider=dict(visible=False)
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=0.5,
            gridcolor='rgba(128,128,128,0.1)',
            side='right',
            color='#666666',
            title_font=dict(size=10)
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=10, r=10, t=20, b=10)
    )

    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(tickfont=dict(size=9))

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="main_candlestick_chart"
    )

    if len(filtered_data) > 0:
        last_row = filtered_data.iloc[-1]
        change_pct = (
            (last_row['Close'] - last_row['Open']) / last_row['Open'] * 100)

        st.markdown("""
        <div style="font-size: 0.9rem; margin-top: 5px;">
            <div style="display: flex; flex-wrap: wrap; gap: 15px;">
                <div><strong>Open:</strong> ${:,.2f}</div>
                <div><strong>High:</strong> ${:,.2f}</div>
                <div><strong>Low:</strong> ${:,.2f}</div>
                <div><strong>Close:</strong> ${:,.2f}</div>
                <div><strong>Change:</strong> <span style="color: {};">{:.2f}%</span></div>
            </div>
        </div>
        """.format(
            last_row['Open'], last_row['High'], last_row['Low'],
            last_row['Close'],
            '#27ae60' if change_pct >= 0 else '#c0392b',
            change_pct
        ), unsafe_allow_html=True)

    # Close wrapper container
    st.markdown("</div>", unsafe_allow_html=True)

    return selected_period


def _filter_data_by_period(data, period):

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
    else:
        start_date = data.index[0]

    return data[data.index >= start_date]
