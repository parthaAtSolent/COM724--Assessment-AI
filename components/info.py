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

    # ----------------------------
    # Minimal Line Chart (Close)
    # ----------------------------
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
        height=140,  # <-- matches card content nicely
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )

    # ----------------------------
    # ONE Card Container
    # ----------------------------
    col1, col2 = st.columns([1.2, 1], gap="medium")

    with col1:
        st.markdown(
            f"""
            <div class="card info-card">
                <div style="display:flex; flex-direction:column; gap:6px;">
                    <span class="info-label">{selected_crypto.upper()}</span>
                    <span style="font-size:28px; font-weight:600;">
                        ${latest_close:,.2f}
                    </span>
                    <span style="color:{change_color}; font-size:14px;">
                        {sign}{pct_change:.2f}%
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )
