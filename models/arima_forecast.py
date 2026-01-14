import streamlit as st
import pandas as pd
import numpy as np
import warnings
import plotly.graph_objects as go

from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error

warnings.filterwarnings("ignore")


def arima_forecast(data, period, n_years, selected_name):
    st.subheader("📈 ARIMA Forecasting")

    # Use only Close price (as in notebook)
    series = data["Close"].dropna()

    # Train / test split (80/20)
    train_size = int(len(series) * 0.8)
    train, test = series[:train_size], series[train_size:]

    st.info(f"Train size: {len(train)} | Test size: {len(test)}")

    with st.spinner("Training Auto-ARIMA model..."):
        auto_model = auto_arima(
            train,
            seasonal=False,
            stepwise=True,
            suppress_warnings=True
        )

    # Fit ARIMA using best order
    model = ARIMA(series, order=auto_model.order)
    model_fit = model.fit()

    # Test predictions
    test_pred = auto_model.predict(n_periods=len(test))

    rmse = np.sqrt(mean_squared_error(test, test_pred))
    mae = mean_absolute_error(test, test_pred)

    col1, col2 = st.columns(2)
    col1.metric("RMSE", f"{rmse:.2f}")
    col2.metric("MAE", f"{mae:.2f}")

    # Forecast future
    forecast = model_fit.forecast(steps=period)

    future_dates = pd.date_range(
        start=series.index[-1],
        periods=period + 1,
        freq="D"
    )[1:]

    # Plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=series.index,
        y=series,
        name="Historical",
        line=dict(width=2)
    ))
    fig.add_trace(go.Scatter(
        x=test.index,
        y=test_pred,
        name="Test Prediction",
        line=dict(dash="dash")
    ))
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=forecast,
        name="Forecast",
        line=dict(width=3)
    ))

    fig.update_layout(
        title=f"ARIMA Forecast – {selected_name}",
        xaxis_title="Date",
        yaxis_title="Price",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Forecast table
    forecast_df = pd.DataFrame({
        "Date": future_dates,
        "Forecast": forecast.values
    }).set_index("Date")

    st.subheader("📊 Forecast Values")
    st.dataframe(forecast_df.tail(10))
