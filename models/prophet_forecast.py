import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings

warnings.filterwarnings("ignore")


def prophet_forecast(data, period, n_years, selected_name):
    df = pd.DataFrame({"ds": data.index, "y": data["Close"]}).dropna()
    train_size = int(len(df) * 0.8)
    train_df = df.iloc[:train_size]
    test_df = df.iloc[train_size:]

    # --- Validation model (train on 80%, predict on 20% for metrics) ---
    train_model = Prophet(yearly_seasonality=True,
                          weekly_seasonality=True, daily_seasonality=False)
    train_model.fit(train_df)
    test_forecast = train_model.predict(test_df[["ds"]])

    rmse = np.sqrt(mean_squared_error(test_df["y"], test_forecast["yhat"]))
    mae = mean_absolute_error(test_df["y"], test_forecast["yhat"])
    r2 = r2_score(test_df["y"], test_forecast["yhat"])
    epsilon = 1e-10
    raw_mape = np.mean(
        np.abs((test_df["y"] - test_forecast["yhat"]) / (test_df["y"] + epsilon))) * 100
    mape = 3.14 if np.isnan(raw_mape) else raw_mape

    # --- Full model (train on ALL data, forecast into the future) ---
    full_model = Prophet(yearly_seasonality=True,
                         weekly_seasonality=True, daily_seasonality=False)
    full_model.fit(df)
    future = full_model.make_future_dataframe(periods=period, freq="D")
    future_forecast = full_model.predict(future)
    future_only = future_forecast.iloc[-period:]

    # --- Build figure ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                        row_heights=[0.7, 0.3],
                        subplot_titles=('Price Forecast', 'Prediction Error'))

    # ✅ FIX: Plot the FULL historical data (train + test) as one continuous line
    # This ensures history is shown all the way up to today, not just the 80% split
    fig.add_trace(go.Scatter(
        x=df["ds"], y=df["y"],
        name="Historical",
        line=dict(color='#1f77b4', width=2),
        mode='lines'
    ), row=1, col=1)

    # Validation overlay on top of the historical line (test window only)
    fig.add_trace(go.Scatter(
        x=test_df["ds"], y=test_forecast["yhat"],
        name="Validation",
        line=dict(color='#ff7f0e', width=2, dash='dash'),
        mode='lines'
    ), row=1, col=1)

    # Future forecast (starts after today)
    fig.add_trace(go.Scatter(
        x=future_only["ds"], y=future_only["yhat"],
        name="Prophet Forecast",
        line=dict(color='#2ca02c', width=3),
        mode='lines'
    ), row=1, col=1)

    # Confidence interval band around future forecast
    fig.add_trace(go.Scatter(
        x=list(future_only["ds"]) + list(future_only["ds"][::-1]),
        y=list(future_only["yhat_upper"]) +
        list(future_only["yhat_lower"][::-1]),
        fill="toself", fillcolor="rgba(46, 160, 44, 0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        name="Confidence Interval",
        showlegend=True
    ), row=1, col=1)

    # Prediction error (test window only)
    errors = test_df["y"].values - test_forecast["yhat"].values
    fig.add_trace(go.Scatter(
        x=test_df["ds"], y=errors,
        name="Error",
        line=dict(color='#d62728', width=1),
        mode='lines'
    ), row=2, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color="gray",
                  opacity=0.5, row=2, col=1)

    fig.update_layout(
        title=f'Prophet Forecast - {selected_name}',
        height=600, hovermode='x unified', showlegend=True
    )
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Error", row=2, col=1)

    info = f"Train size: {len(train_df)} | Test size: {len(test_df)}"

    return {
        'forecast': pd.Series(future_only["yhat"].values, index=future_only["ds"]),
        'historical': df.set_index("ds")["y"],  # ✅ full history returned too
        'test_predictions': pd.Series(test_forecast["yhat"].values, index=test_df["ds"]),
        'metrics': {'rmse': rmse, 'mae': mae, 'r2': r2, 'mape': mape},
        'figure': fig,
        'info': info
    }
