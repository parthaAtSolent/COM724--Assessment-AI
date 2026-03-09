import streamlit as st
import plotly.graph_objects as go


def render_info_section(data, selected_crypto):
    if data is None or data.empty or len(data) < 2:
        return

    latest = data.iloc[-1]
    previous = data.iloc[-2]

    latest_close = latest["Close"]
    prev_close = previous["Close"]

    pct_change = ((latest_close - prev_close) / prev_close) * 100
    change_color = "#16a34a" if pct_change >= 0 else "#dc2626"
    sign = "+" if pct_change >= 0 else ""

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["Close"],
            mode="lines",
            line=dict(width=2, color="#7c3aed"),
            hoverinfo="skip"
        )
    )
    fig.update_layout(
        height=150,
        margin=dict(l=12, r=12, t=40, b=12),
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(visible=False),
        yaxis=dict(
            visible=False,
            range=[data["Close"].min() * 0.95, data["Close"].max() * 1.05]
        )
    )

    col1, col2 = st.columns([1.2, 1.8], gap="small")

    with col1:
        st.markdown(
            f"""
            <div class="card info-card" style="
                display: flex;
                flex-direction: column;
                justify-content: center;
                height: 183px;
                padding: 12px 16px;
                box-sizing: border-box;
                background-color: #ffffff;
                border-radius: 14px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
            ">
                <span style="font-size:18px; color:#888; margin-bottom:4px; text-transform:uppercase; letter-spacing:0.5px;">
                    {selected_crypto.upper()}
                </span>
                <span style="font-size:32px; font-weight:600; line-height:1.2; color:#111;">
                    ${latest_close:,.2f}
                </span>
                <span style="color:{change_color}; font-size:18px; margin-top:4px; font-weight:500;">
                    {sign}{pct_change:.2f}%
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        with st.container():

            st.markdown(f"""
            <style>

            /* ONLY style the info chart */
            div[data-testid="stPlotlyChart"]:has(div#info_chart_{selected_crypto}) {{
                background-color: #ffffff !important;
                border-radius: 14px !important;
                box-shadow: 0 8px 24px rgba(0,0,0,0.06) !important;
                padding: 6px !important;
                height: 183px !important;
                overflow: hidden !important;
            }}

            div[data-testid="stPlotlyChart"]:has(div#info_chart_{selected_crypto}) .js-plotly-plot {{
                height: 100% !important;
                width: 100% !important;
            }}

            </style>
            """, unsafe_allow_html=True)

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
                key=f"info_chart_{selected_crypto}"
            )
