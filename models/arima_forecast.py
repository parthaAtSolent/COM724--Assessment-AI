from statsmodels.tsa.stattools import adfuller
import streamlit as st
import pandas as pd
import numpy as np
import warnings
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

warnings.filterwarnings("ignore")


def arima_forecast(data, period, n_years, selected_name):
    series = data["Close"].dropna()
    train_size = int(len(series) * 0.8)
    train, test = series[:train_size], series[train_size:]

    auto_model = auto_arima(train, seasonal=False,
                            stepwise=True, suppress_warnings=True)
    model = ARIMA(series, order=auto_model.order)
    model_fit = model.fit()

    test_pred = auto_model.predict(n_periods=len(test))

    rmse = np.sqrt(mean_squared_error(test, test_pred))
    mae = mean_absolute_error(test, test_pred)
    r2 = r2_score(test, test_pred)
    epsilon = 1e-10
    mape = np.mean(np.abs((test.values - test_pred) /
                   (test.values + epsilon))) * 100

    forecast = model_fit.forecast(steps=period)
    future_dates = pd.date_range(
        start=series.index[-1] + pd.Timedelta(days=1), periods=period, freq="D"
    )

    # Build figure
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                        row_heights=[0.7, 0.3],
                        subplot_titles=('Price Forecast', 'Prediction Error'))

    fig.add_trace(go.Scatter(x=series.index, y=series, name="Historical",
                             line=dict(color='#1f77b4', width=2), mode='lines'), row=1, col=1)
    fig.add_trace(go.Scatter(x=test.index, y=test_pred, name="Validation",
                             line=dict(color='#ff7f0e', width=2, dash='dash'), mode='lines'), row=1, col=1)
    fig.add_trace(go.Scatter(x=future_dates, y=forecast, name="ARIMA Forecast",
                             line=dict(color='#2ca02c', width=3), mode='lines'), row=1, col=1)
    errors = test.values - test_pred
    fig.add_trace(go.Scatter(x=test.index, y=errors, name="Error",
                             line=dict(color='#d62728', width=1), mode='lines'), row=2, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color="gray",
                  opacity=0.5, row=2, col=1)

    fig.update_layout(
        title=f'ARIMA({auto_model.order[0]},{auto_model.order[1]},{auto_model.order[2]}) Forecast - {selected_name}',
        height=600, hovermode='x unified', showlegend=True
    )
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Error", row=2, col=1)

    info = f"Train size: {len(train)} | Test size: {len(test)} | ARIMA Order: {auto_model.order}"

    return {
        'forecast': pd.Series(forecast, index=future_dates),
        'historical': series,
        'test_predictions': pd.Series(test_pred, index=test.index),
        'metrics': {'rmse': rmse, 'mae': mae, 'r2': r2, 'mape': mape},
        'order': auto_model.order,
        'figure': fig,
        'info': info
    }
