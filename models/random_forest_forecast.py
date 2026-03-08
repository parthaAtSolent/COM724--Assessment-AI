import time
from sklearn.model_selection import TimeSeriesSplit
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')


def random_forest_forecast(data, period, n_years, selected_name, confidence_interval=None):
    # Prepare data
    df = data[['Close']].copy()

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

        # Process data in background
        print("Preparing features for Random Forest model...")

        # Create lag features
        lag_periods = [1, 2, 3, 5, 7, 14, 21, 30]
        for lag in lag_periods:
            df[f'lag_{lag}'] = df['Close'].shift(lag)

        # Create moving average and standard deviation features
        for window in [7, 14, 30, 60]:
            df[f'ma_{window}'] = df['Close'].rolling(window=window).mean()
            df[f'std_{window}'] = df['Close'].rolling(window=window).std()

        df['close_ma7_ratio'] = df['Close'] / df['ma_7']
        df['close_ma30_ratio'] = df['Close'] / df['ma_30']
        df['volatility'] = df['Close'].rolling(window=7).std()
        df = df.dropna()

        X = df.drop('Close', axis=1)
        y = df['Close']
        dates = df.index

        # Time-series split
        tscv = TimeSeriesSplit(n_splits=5)
        y_true_all, y_pred_all, dates_all = [], [], []
        model = RandomForestRegressor(
            n_estimators=200, random_state=42, n_jobs=-1)

        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_true_all.extend(y_test.values)
            y_pred_all.extend(y_pred)
            dates_all.extend(X_test.index)

        y_true_all, y_pred_all = np.array(y_true_all), np.array(y_pred_all)
        rmse = np.sqrt(mean_squared_error(y_true_all, y_pred_all))
        mae = mean_absolute_error(y_true_all, y_pred_all)
        r2 = r2_score(y_true_all, y_pred_all)
        mape = np.mean(np.abs((y_true_all - y_pred_all) / y_true_all)) * 100

        # Forecast future
        future_predictions = []
        last_features = X.iloc[-1:].copy()

        # Initialize a list to keep track of all predictions (for moving averages)
        # Keep last 60 days for MA calculations
        all_predictions = list(df['Close'].values[-60:])

        for _ in range(period):
            next_pred = model.predict(last_features)[0]
            future_predictions.append(next_pred)
            all_predictions.append(next_pred)  # Add to all predictions list

            # Create new features for next prediction
            new_features = last_features.copy()

            # Update lag features
            for lag in lag_periods:
                col_name = f'lag_{lag}'
                if col_name in new_features.columns:
                    if lag == 1:
                        new_features[col_name] = next_pred
                    else:
                        # For lag > 1, we need to shift previous predictions
                        # This is complex because we need to track multiple steps
                        # Simplified approach: use the last available value
                        prev_lag = lag - 1
                        if prev_lag in lag_periods:
                            new_features[col_name] = last_features[f'lag_{prev_lag}'].values[0]

            # Update moving averages
            for window in [7, 14, 30, 60]:
                ma_col = f'ma_{window}'
                std_col = f'std_{window}'

                if ma_col in new_features.columns:
                    if len(all_predictions) >= window:
                        window_values = all_predictions[-window:]
                        new_features[ma_col] = np.mean(window_values)
                        if std_col in new_features.columns:
                            new_features[std_col] = np.std(window_values)

            # Update ratios
            if 'ma_7' in new_features.columns and 'close_ma7_ratio' in new_features.columns:
                if len(all_predictions) >= 7:
                    new_features['close_ma7_ratio'] = next_pred / \
                        new_features['ma_7'].values[0]

            if 'ma_30' in new_features.columns and 'close_ma30_ratio' in new_features.columns:
                if len(all_predictions) >= 30:
                    new_features['close_ma30_ratio'] = next_pred / \
                        new_features['ma_30'].values[0]

            # Update volatility
            if 'volatility' in new_features.columns:
                if len(all_predictions) >= 7:
                    new_features['volatility'] = np.std(all_predictions[-7:])

            last_features = new_features

        future_dates = pd.date_range(
            start=dates[-1] + pd.Timedelta(days=1), periods=period, freq='D')

        # Now display the actual content
        st.subheader(f"{selected_name}")

        # Clear the skeleton
        skeleton_placeholder.empty()

        # Now display the actual content
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("RMSE", f"{rmse:.2f}")
        with col2:
            st.metric("MAE", f"{mae:.2f}")
        with col3:
            st.metric("R² Score", f"{r2:.4f}")
        with col4:
            st.metric("MAPE", f"{mape:.2f}%")

        # Create the actual chart
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                            row_heights=[0.7, 0.3],
                            subplot_titles=('Price Forecast', 'Prediction Error'))

        # Historical data
        fig.add_trace(go.Scatter(x=dates, y=y, mode='lines', name='Historical',
                      line=dict(color='#1f77b4', width=2)), row=1, col=1)

        # Validation predictions
        fig.add_trace(go.Scatter(x=dates_all, y=y_pred_all, mode='lines', name='Validation',
                      line=dict(color='#ff7f0e', width=2, dash='dash')), row=1, col=1)

        # Future forecast
        fig.add_trace(go.Scatter(x=future_dates, y=future_predictions, mode='lines',
                      name='RF Forecast', line=dict(color='#2ca02c', width=3)), row=1, col=1)

        # Error plot
        errors = y_true_all - y_pred_all
        fig.add_trace(go.Scatter(x=dates_all, y=errors, mode='lines',
                      name='Error', line=dict(color='#d62728', width=1)), row=2, col=1)

        fig.add_hline(y=0, line_dash="dash", line_color="gray",
                      opacity=0.5, row=2, col=1)

        fig.update_layout(
            title=f'{selected_name} - Random Forest Forecast',
            height=600,
            hovermode='x unified',
            showlegend=True
        )

        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
        fig.update_yaxes(title_text="Error", row=2, col=1)

        st.plotly_chart(fig, use_container_width=True)

    return {
        'forecast': pd.Series(future_predictions, index=future_dates),
        'historical': y,
        'test_predictions': pd.Series(y_pred_all, index=dates_all),
        'metrics': {'rmse': rmse, 'mae': mae, 'r2': r2, 'mape': mape}
    }
