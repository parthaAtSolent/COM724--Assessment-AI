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


def check_stationarity(timeseries, alpha=0.05, show_output=True):
    """
    Perform Augmented Dickey-Fuller test to check stationarity.

    Returns:
        is_stationary (bool)
        p_value (float)
        adf_stat (float)
    """
    result = adfuller(timeseries.dropna(), autolag='AIC')
    adf_stat, p_value = result[0], result[1]

    if show_output:
        st.write("### 🔍 Stationarity Test (ADF)")
        st.write(f"**ADF Statistic:** {adf_stat:.4f}")
        st.write(f"**p-value:** {p_value:.6f}")

        if p_value <= alpha:
            st.success("✅ Series is stationary")
        else:
            st.warning("⚠️ Series is NOT stationary")

    return p_value <= alpha, p_value, adf_stat


def make_stationary(series, max_diff=2):
    """
    Applies differencing until the series becomes stationary
    or max_diff is reached.

    Returns:
        stationary_series (pd.Series)
        d (int) -> number of differences applied
    """
    d = 0
    temp_series = series.copy()

    is_stationary, _, _ = check_stationarity(temp_series)

    while not is_stationary and d < max_diff:
        d += 1
        temp_series = temp_series.diff().dropna()
        is_stationary, _, _ = check_stationarity(temp_series)

    return temp_series, d


def arima_forecast(data, period, n_years, selected_name):
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

        # Original series
        series = data["Close"].dropna()

        # # Check & enforce stationarity
        # series, d = make_stationary(series)

        # st.info(f"📉 Differencing applied: d = {d}")

        # Train / test split (80/20)
        train_size = int(len(series) * 0.8)
        train, test = series[:train_size], series[train_size:]

        # Train Auto-ARIMA model
        auto_model = auto_arima(
            train,
            seasonal=False,
            stepwise=True,
            suppress_warnings=True
        )

        # Fit ARIMA using best order on full series
        model = ARIMA(series, order=auto_model.order)
        model_fit = model.fit()

        # Test predictions
        test_pred = auto_model.predict(n_periods=len(test))

        # Calculate all metrics
        rmse = np.sqrt(mean_squared_error(test, test_pred))
        mae = mean_absolute_error(test, test_pred)
        r2 = r2_score(test, test_pred)

        # Calculate MAPE (with small epsilon to avoid division by zero)
        epsilon = 1e-10
        mape = np.mean(np.abs((test.values - test_pred) /
                       (test.values + epsilon))) * 100

        # Forecast future
        forecast = model_fit.forecast(steps=period)

        future_dates = pd.date_range(
            start=series.index[-1] + pd.Timedelta(days=1),
            periods=period,
            freq="D"
        )

        # Clear the skeleton
        skeleton_placeholder.empty()

        # Now display the actual content
        st.subheader(f"📈 ARIMA Forecast - {selected_name}")

        # Display model info
        st.info(
            f"Train size: {len(train)} | Test size: {len(test)} | ARIMA Order: {auto_model.order}")

        # Display metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("RMSE", f"{rmse:.2f}")
        with col2:
            st.metric("MAE", f"{mae:.2f}")
        with col3:
            st.metric("R² Score", f"{r2:.4f}")
        with col4:
            st.metric("MAPE", f"{mape:.2f}%")

        # Create the actual chart with subplots
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                            row_heights=[0.7, 0.3],
                            subplot_titles=('Price Forecast', 'Prediction Error'))

        # Historical data
        fig.add_trace(go.Scatter(
            x=series.index,
            y=series,
            name="Historical",
            line=dict(color='#1f77b4', width=2),
            mode='lines'
        ), row=1, col=1)

        # Test predictions
        fig.add_trace(go.Scatter(
            x=test.index,
            y=test_pred,
            name="Validation",
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            mode='lines'
        ), row=1, col=1)

        # Future forecast
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=forecast,
            name="ARIMA Forecast",
            line=dict(color='#2ca02c', width=3),
            mode='lines'
        ), row=1, col=1)

        # Error plot
        errors = test.values - test_pred
        fig.add_trace(go.Scatter(
            x=test.index,
            y=errors,
            name="Error",
            line=dict(color='#d62728', width=1),
            mode='lines'
        ), row=2, col=1)

        fig.add_hline(y=0, line_dash="dash", line_color="gray",
                      opacity=0.5, row=2, col=1)

        fig.update_layout(
            title=f'ARIMA({auto_model.order[0]},{auto_model.order[1]},{auto_model.order[2]}) Forecast - {selected_name}',
            height=600,
            hovermode='x unified',
            showlegend=True
        )

        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
        fig.update_yaxes(title_text="Error", row=2, col=1)

        st.plotly_chart(fig, use_container_width=True)

        # Forecast table
        with st.expander("📊 View Forecast Values"):
            forecast_df = pd.DataFrame({
                "Date": future_dates,
                "Forecast": forecast.values
            }).set_index("Date")
            st.dataframe(forecast_df)

    return {
        'forecast': pd.Series(forecast.values, index=future_dates),
        'historical': series,
        'test_predictions': pd.Series(test_pred, index=test.index),
        'metrics': {'rmse': rmse, 'mae': mae, 'r2': r2, 'mape': mape},
        'order': auto_model.order
    }
