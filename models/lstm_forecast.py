import os
import warnings
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from keras.models import Sequential
from keras.layers import LSTM, Dense
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


@st.cache_resource
def build_lstm(sequence_length):
    model = Sequential([
        LSTM(16, input_shape=(sequence_length, 1)),
        Dense(1)
    ])
    model.compile(optimizer=Adam(0.001), loss="mse")
    return model


def lstm_forecast(data, period, n_years, selected_name, sequence_length=15):
    # Create skeleton container for the entire chart section
    with st.container():
        # Create placeholder for skeleton
        skeleton_placeholder = st.empty()

        # Show skeleton while processing
        with skeleton_placeholder.container():
            st.markdown("""
            <style>
            .skeleton {
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
                border-radius: 8px;
                margin-bottom: 10px;
            }
            
            .skeleton-header {
                height: 30px;
                width: 250px;
                margin-bottom: 20px;
            }
            
            .skeleton-metrics {
                display: flex;
                gap: 15px;
                margin-bottom: 20px;
            }
            
            .skeleton-metric {
                height: 70px;
                flex: 1;
                border-radius: 6px;
            }
            
            .skeleton-chart {
                height: 400px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            
            .skeleton-error {
                height: 150px;
                border-radius: 8px;
            }
            
            @keyframes loading {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }
            </style>
            """, unsafe_allow_html=True)

            # Skeleton header
            st.markdown('<div class="skeleton skeleton-header"></div>',
                        unsafe_allow_html=True)

            # Skeleton metrics
            st.markdown('<div class="skeleton-metrics">' +
                        ''.join(['<div class="skeleton skeleton-metric"></div>' for _ in range(4)]) +
                        '</div>', unsafe_allow_html=True)

            # Skeleton chart area
            st.markdown('<div class="skeleton skeleton-chart"></div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="skeleton skeleton-error"></div>',
                        unsafe_allow_html=True)

        # ----- Actual computation happens here -----
        series = data[["Close"]].dropna()

        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(series)

        X, y = [], []
        for i in range(sequence_length, len(scaled)):
            X.append(scaled[i-sequence_length:i, 0])
            y.append(scaled[i, 0])

        X, y = np.array(X), np.array(y)
        X = X.reshape(X.shape[0], X.shape[1], 1)

        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        model = build_lstm(sequence_length)

        # Much faster training
        model.fit(
            X_train, y_train,
            epochs=5,
            batch_size=32,
            verbose=0
        )

        test_pred = model.predict(X_test, verbose=0)

        y_test_inv = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()
        test_pred_inv = scaler.inverse_transform(test_pred).flatten()

        test_dates = series.index[
            train_size + sequence_length:
            train_size + sequence_length + len(test_pred_inv)
        ]

        rmse = np.sqrt(mean_squared_error(y_test_inv, test_pred_inv))
        mae = mean_absolute_error(y_test_inv, test_pred_inv)
        r2 = r2_score(y_test_inv, test_pred_inv)

        epsilon = 1e-10
        mape = np.mean(np.abs((y_test_inv - test_pred_inv) /
                       (y_test_inv + epsilon))) * 100

        # Simple future prediction
        future_preds = []
        current_seq = scaled[-sequence_length:].reshape(1, sequence_length, 1)

        for _ in range(period):
            next_pred = model.predict(current_seq, verbose=0)
            future_preds.append(next_pred[0, 0])

            current_seq = np.append(
                current_seq[:, 1:, :],
                next_pred.reshape(1, 1, 1),
                axis=1
            )

        future_preds = scaler.inverse_transform(
            np.array(future_preds).reshape(-1, 1)
        ).flatten()

        future_dates = pd.date_range(
            start=series.index[-1] + pd.Timedelta(days=1),
            periods=period,
            freq="D"
        )

        # Clear the skeleton
        skeleton_placeholder.empty()

        # --- Build figure (actual content) ---
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.3],
            subplot_titles=('Price Forecast', 'Prediction Error')
        )

        fig.add_trace(go.Scatter(
            x=series.index, y=series["Close"],
            name="Historical",
            line=dict(color='#1f77b4', width=2),
            mode='lines'
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=test_dates, y=test_pred_inv,
            name="Validation",
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            mode='lines'
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=future_dates, y=future_preds,
            name="LSTM Forecast",
            line=dict(color='#2ca02c', width=3),
            mode='lines'
        ), row=1, col=1)

        errors = y_test_inv - test_pred_inv

        fig.add_trace(go.Scatter(
            x=test_dates, y=errors,
            name="Error",
            line=dict(color='#d62728', width=1),
            mode='lines'
        ), row=2, col=1)

        fig.add_hline(y=0, line_dash="dash", line_color="gray",
                      opacity=0.5, row=2, col=1)

        fig.update_layout(
            # title=f'LSTM Forecast - {selected_name}',
            height=500,
            hovermode='x unified',
            # Reduced margins
            showlegend=True, margin=dict(l=40, r=40, t=40, b=40)
        )

        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
        fig.update_yaxes(title_text="Error", row=2, col=1)

        info = f"Train sequences: {len(X_train)} | Test sequences: {len(X_test)} | Sequence length: {sequence_length}"

        return {
            'forecast': pd.Series(future_preds, index=future_dates),
            'historical': series['Close'],
            'test_predictions': pd.Series(test_pred_inv, index=test_dates),
            'metrics': {'rmse': rmse, 'mae': mae, 'r2': r2, 'mape': mape},
            'figure': fig,
            'info': info
        }
