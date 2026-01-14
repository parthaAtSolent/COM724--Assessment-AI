import os
import warnings
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


@st.cache_resource
def build_lstm(sequence_length):
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(sequence_length, 1)),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer=Adam(0.001), loss="mse")
    return model


def lstm_forecast(data, period, n_years, selected_name, sequence_length=60):
    st.subheader("🧠 LSTM Forecasting")

    # Use Close price only
    series = data[["Close"]].dropna()

    # Scale data
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(series)

    # Create sequences
    X, y = [], []
    for i in range(sequence_length, len(scaled)):
        X.append(scaled[i-sequence_length:i, 0])
        y.append(scaled[i, 0])

    X, y = np.array(X), np.array(y)
    X = X.reshape(X.shape[0], X.shape[1], 1)

    # Train / test split
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    st.info(f"Train sequences: {len(X_train)} | Test sequences: {len(X_test)}")

    with st.spinner("Training LSTM model..."):
        model = build_lstm(sequence_length)
        model.fit(
            X_train,
            y_train,
            epochs=20,
            batch_size=32,
            verbose=0
        )

    # Predictions
    test_pred = model.predict(X_test, verbose=0)

    y_test_inv = scaler.inverse_transform(y_test.reshape(-1, 1))
    test_pred_inv = scaler.inverse_transform(test_pred)

    rmse = np.sqrt(mean_squared_error(y_test_inv, test_pred_inv))
    mae = mean_absolute_error(y_test_inv, test_pred_inv)

    col1, col2 = st.columns(2)
    col1.metric("RMSE", f"{rmse:.2f}")
    col2.metric("MAE", f"{mae:.2f}")

    # Future forecasting
    future_preds = []
    current_seq = scaled[-sequence_length:].reshape(1, sequence_length, 1)

    for _ in range(period):
        next_val = model.predict(current_seq, verbose=0)
        future_preds.append(next_val[0, 0])
        current_seq = np.append(
            current_seq[:, 1:, :],
            next_val.reshape(1, 1, 1),
            axis=1
        )

    future_preds = scaler.inverse_transform(
        np.array(future_preds).reshape(-1, 1)
    ).flatten()

    future_dates = pd.date_range(
        start=series.index[-1],
        periods=period + 1,
        freq="D"
    )[1:]

    # Plot

    # Build correct test dates
    test_dates = series.index[
        train_size + sequence_length:
        train_size + sequence_length + len(test_pred_inv)
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=series.index,
        y=series["Close"],
        name="Historical",
        line=dict(width=2)
    ))

    fig.add_trace(go.Scatter(
        x=test_dates,
        y=test_pred_inv.flatten(),
        name="Test Prediction",
        line=dict(dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=future_dates,
        y=future_preds,
        name="Forecast",
        line=dict(width=3, dash="dash")
    ))

    fig.update_layout(
        title=f"LSTM Forecast – {selected_name}",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Forecast table
    forecast_df = pd.DataFrame(
        {"Forecast": future_preds},
        index=future_dates
    )

    st.subheader("📊 Forecast Values")
    st.dataframe(forecast_df.tail(10))
