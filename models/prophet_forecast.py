import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings

warnings.filterwarnings("ignore")


def prophet_forecast(data, period, n_years, selected_name):
    st.subheader("📈 Prophet Forecasting")

    # ----- Prepare data -----
    df = pd.DataFrame({
        "ds": data.index,
        "y": data["Close"]
    }).dropna()

    # ----- Train / test split -----
    train_size = int(len(df) * 0.8)
    train_df = df.iloc[:train_size]
    test_df = df.iloc[train_size:]

    st.info(f"Train size: {len(train_df)} | Test size: {len(test_df)}")

    # =========================
    # 1️⃣ TRAIN MODEL (TRAIN ONLY)
    # =========================
    with st.spinner("Training Prophet model..."):
        train_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )
        train_model.fit(train_df)

    # ----- Test prediction (BACKTEST) -----
    test_forecast = train_model.predict(test_df[["ds"]])

    rmse = np.sqrt(mean_squared_error(test_df["y"], test_forecast["yhat"]))
    mae = mean_absolute_error(test_df["y"], test_forecast["yhat"])

    col1, col2 = st.columns(2)
    col1.metric("RMSE", f"{rmse:.2f}")
    col2.metric("MAE", f"{mae:.2f}")

    # =========================
    # 2️⃣ REFIT ON FULL DATA (FUTURE ONLY)
    # =========================
    with st.spinner("Refitting model for future forecast..."):
        full_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )
        full_model.fit(df)

    future = full_model.make_future_dataframe(periods=period, freq="D")
    future_forecast = full_model.predict(future)

    future_only = future_forecast.iloc[-period:]

    # =========================
    # 3️⃣ PLOT (STRICTLY ALIGNED)
    # =========================
    fig = go.Figure()

    # Historical
    fig.add_trace(go.Scatter(
        x=train_df["ds"],
        y=train_df["y"],
        name="Historical",
        line=dict(width=2)
    ))

    # Test prediction
    fig.add_trace(go.Scatter(
        x=test_df["ds"],
        y=test_forecast["yhat"],
        name="Test Prediction",
        line=dict(dash="dash")
    ))

    # Future forecast
    fig.add_trace(go.Scatter(
        x=future_only["ds"],
        y=future_only["yhat"],
        name="Forecast",
        line=dict(width=3, dash="dash")
    ))

    # Confidence interval (FUTURE ONLY)
    fig.add_trace(go.Scatter(
        x=list(future_only["ds"]) + list(future_only["ds"][::-1]),
        y=list(future_only["yhat_upper"]) +
        list(future_only["yhat_lower"][::-1]),
        fill="toself",
        fillcolor="rgba(0, 0, 255, 0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        name="Confidence Interval"
    ))

    fig.update_layout(
        title=f"Prophet Forecast – {selected_name}",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 4️⃣ FORECAST TABLE
    # =========================
    forecast_df = future_only[["ds", "yhat"]].set_index("ds")
    forecast_df.columns = ["Forecast"]

    st.subheader("📊 Forecast Values")
    st.dataframe(forecast_df.tail(10))
