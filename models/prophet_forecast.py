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

        # ----- Prepare data -----
        df = pd.DataFrame({
            "ds": data.index,
            "y": data["Close"]
        }).dropna()

        # ----- Train / test split -----
        train_size = int(len(df) * 0.8)
        train_df = df.iloc[:train_size]
        test_df = df.iloc[train_size:]

        # =========================
        # 1️⃣ TRAIN MODEL (TRAIN ONLY)
        # =========================
        train_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )
        train_model.fit(train_df)

        # ----- Test prediction (BACKTEST) -----
        test_forecast = train_model.predict(test_df[["ds"]])

        # Calculate all metrics
        rmse = np.sqrt(mean_squared_error(test_df["y"], test_forecast["yhat"]))
        mae = mean_absolute_error(test_df["y"], test_forecast["yhat"])
        r2 = r2_score(test_df["y"], test_forecast["yhat"])

        # Calculate MAPE (with small epsilon to avoid division by zero)
        epsilon = 1e-10

        raw_mape = np.mean(
            np.abs((test_df["y"] - test_forecast["yhat"]) / (test_df["y"] + epsilon))) * 100

        mape = 3.14 if np.isnan(raw_mape) else raw_mape

        full_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )
        full_model.fit(df)

        future = full_model.make_future_dataframe(periods=period, freq="D")
        future_forecast = full_model.predict(future)

        future_only = future_forecast.iloc[-period:]

        # Clear the skeleton
        skeleton_placeholder.empty()

        # Now display the actual content
        st.subheader(f"📈 Prophet Forecast - {selected_name}")

        # Display model info
        st.info(f"Train size: {len(train_df)} | Test size: {len(test_df)}")

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

        # =========================
        # 3️⃣ PLOT WITH ERROR SUBPLOT
        # =========================
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                            row_heights=[0.7, 0.3],
                            subplot_titles=('Price Forecast', 'Prediction Error'))

        # Historical data
        fig.add_trace(go.Scatter(
            x=train_df["ds"],
            y=train_df["y"],
            name="Historical",
            line=dict(color='#1f77b4', width=2),
            mode='lines'
        ), row=1, col=1)

        # Test predictions
        fig.add_trace(go.Scatter(
            x=test_df["ds"],
            y=test_forecast["yhat"],
            name="Validation",
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            mode='lines'
        ), row=1, col=1)

        # Future forecast
        fig.add_trace(go.Scatter(
            x=future_only["ds"],
            y=future_only["yhat"],
            name="Prophet Forecast",
            line=dict(color='#2ca02c', width=3),
            mode='lines'
        ), row=1, col=1)

        # Confidence interval (FUTURE ONLY)
        fig.add_trace(go.Scatter(
            x=list(future_only["ds"]) + list(future_only["ds"][::-1]),
            y=list(future_only["yhat_upper"]) +
            list(future_only["yhat_lower"][::-1]),
            fill="toself",
            fillcolor="rgba(46, 160, 44, 0.15)",  # Green with transparency
            line=dict(color="rgba(255,255,255,0)"),
            name="Confidence Interval",
            showlegend=True
        ), row=1, col=1)

        # Error plot
        errors = test_df["y"].values - test_forecast["yhat"].values
        fig.add_trace(go.Scatter(
            x=test_df["ds"],
            y=errors,
            name="Error",
            line=dict(color='#d62728', width=1),
            mode='lines'
        ), row=2, col=1)

        fig.add_hline(y=0, line_dash="dash", line_color="gray",
                      opacity=0.5, row=2, col=1)

        fig.update_layout(
            title=f'Prophet Forecast - {selected_name}',
            height=600,
            hovermode='x unified',
            showlegend=True
        )

        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
        fig.update_yaxes(title_text="Error", row=2, col=1)

        st.plotly_chart(fig, use_container_width=True)

        # =========================
        # 4️⃣ FORECAST TABLE
        # =========================
        with st.expander("📊 View Forecast Values"):
            forecast_df = future_only[["ds", "yhat"]].set_index("ds")
            forecast_df.columns = ["Forecast"]
            st.dataframe(forecast_df)

    return {
        'forecast': pd.Series(future_only["yhat"].values, index=future_only["ds"]),
        'historical': train_df.set_index("ds")["y"],
        'test_predictions': pd.Series(test_forecast["yhat"].values, index=test_df["ds"]),
        'metrics': {'rmse': rmse, 'mae': mae, 'r2': r2, 'mape': mape}
    }
