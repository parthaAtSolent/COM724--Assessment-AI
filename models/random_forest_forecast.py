import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import plotly.graph_objects as go
from utils.config import RF_PARAMS, RF_LOOKBACK_PERIOD, TRAIN_TEST_SPLIT
from utils.helpers import create_future_dates, calculate_metrics


@st.cache_resource
def create_random_forest_model():
    """Create and return a Random Forest model"""
    return RandomForestRegressor(**RF_PARAMS)


def create_features(_data, lookback=RF_LOOKBACK_PERIOD):
    """Create time series features"""
    df = _data.copy()

    # Create lag features
    for i in range(1, lookback + 1):
        df[f'lag_{i}'] = df['Close'].shift(i)

    # Create rolling statistics
    df['rolling_mean_7'] = df['Close'].rolling(window=7).mean()
    df['rolling_std_7'] = df['Close'].rolling(window=7).std()
    df['rolling_mean_30'] = df['Close'].rolling(window=30).mean()
    df['rolling_std_30'] = df['Close'].rolling(window=30).std()
    df['rolling_mean_60'] = df['Close'].rolling(window=60).mean()

    # Price momentum features
    df['price_change_1'] = df['Close'].pct_change(1)
    df['price_change_7'] = df['Close'].pct_change(7)
    df['price_change_30'] = df['Close'].pct_change(30)

    # Date features
    df['day_of_week'] = df['Date'].dt.dayofweek
    df['day_of_month'] = df['Date'].dt.day
    df['month'] = df['Date'].dt.month
    df['quarter'] = df['Date'].dt.quarter
    df['year'] = df['Date'].dt.year
    df['day_of_year'] = df['Date'].dt.dayofyear
    df['week_of_year'] = df['Date'].dt.isocalendar().week

    return df


def random_forest_forecast(data, period, n_years, selected_name):
    """Random Forest forecasting implementation"""
    st.subheader('Random Forest Forecast')

    # Prepare data for Random Forest
    with st.spinner('Preparing data for Random Forest...'):
        rf_data = data[['Date', 'Close']].copy()
        rf_data['Date'] = pd.to_datetime(rf_data['Date'])

        # Create features
        rf_data_featured = create_features(rf_data)
        rf_data_featured = rf_data_featured.dropna()

        # Define features
        feature_columns = [
            col for col in rf_data_featured.columns if col not in ['Date', 'Close']]
        X = rf_data_featured[feature_columns]
        y = rf_data_featured['Close']

        # Split data
        train_size = int(len(X) * TRAIN_TEST_SPLIT)
        X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
        y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
        dates_test = rf_data_featured['Date'].iloc[train_size:]

    # Train Random Forest model
    with st.spinner('Training Random Forest model...'):
        rf_model = create_random_forest_model()
        rf_model.fit(X_train, y_train)

        # Make predictions on test data
        y_pred_test = rf_model.predict(X_test)

    # Forecast future values
    with st.spinner('Generating future forecasts with Random Forest...'):
        future_predictions = []

        # Start with the last row of actual data
        current_features = rf_data_featured.iloc[-1][feature_columns].copy()
        last_date = rf_data_featured['Date'].iloc[-1]
        last_close = rf_data_featured['Close'].iloc[-1]

        # Store recent prices for lag features
        recent_prices = list(rf_data_featured['Close'].iloc[-60:])

        for i in range(period):
            # Prepare feature vector for the next prediction
            feature_dict = {}

            # Update lag features (1-60)
            for lag in range(1, 61):
                if f'lag_{lag}' in feature_columns:
                    if lag == 1:
                        feature_dict[f'lag_{lag}'] = last_close
                    else:
                        feature_dict[f'lag_{lag}'] = recent_prices[-lag +
                                                                   1] if len(recent_prices) >= lag else last_close

            # Calculate rolling statistics from recent prices
            recent_series = pd.Series(recent_prices[-60:] + [last_close])
            if 'rolling_mean_7' in feature_columns:
                feature_dict['rolling_mean_7'] = recent_series.tail(7).mean()
            if 'rolling_std_7' in feature_columns:
                feature_dict['rolling_std_7'] = recent_series.tail(7).std()
            if 'rolling_mean_30' in feature_columns:
                feature_dict['rolling_mean_30'] = recent_series.tail(30).mean()
            if 'rolling_std_30' in feature_columns:
                feature_dict['rolling_std_30'] = recent_series.tail(30).std()
            if 'rolling_mean_60' in feature_columns:
                feature_dict['rolling_mean_60'] = recent_series.mean()

            # Calculate price changes
            if len(recent_prices) >= 2:
                if 'price_change_1' in feature_columns:
                    feature_dict['price_change_1'] = (
                        last_close - recent_prices[-1]) / recent_prices[-1]
                if 'price_change_7' in feature_columns and len(recent_prices) >= 7:
                    feature_dict['price_change_7'] = (
                        last_close - recent_prices[-7]) / recent_prices[-7]
                if 'price_change_30' in feature_columns and len(recent_prices) >= 30:
                    feature_dict['price_change_30'] = (
                        last_close - recent_prices[-30]) / recent_prices[-30]

            # Date features for next day
            next_date = last_date + pd.Timedelta(days=i + 1)
            if 'day_of_week' in feature_columns:
                feature_dict['day_of_week'] = next_date.dayofweek
            if 'day_of_month' in feature_columns:
                feature_dict['day_of_month'] = next_date.day
            if 'month' in feature_columns:
                feature_dict['month'] = next_date.month
            if 'quarter' in feature_columns:
                feature_dict['quarter'] = next_date.quarter
            if 'year' in feature_columns:
                feature_dict['year'] = next_date.year
            if 'day_of_year' in feature_columns:
                feature_dict['day_of_year'] = next_date.dayofyear
            if 'week_of_year' in feature_columns:
                feature_dict['week_of_year'] = next_date.isocalendar().week

            # Convert to DataFrame
            feature_df = pd.DataFrame([feature_dict])[
                feature_columns].fillna(0)

            # Make prediction
            next_pred = rf_model.predict(feature_df)[0]
            future_predictions.append(next_pred)

            # Update for next iteration
            recent_prices.append(next_pred)
            if len(recent_prices) > 60:
                recent_prices.pop(0)
            last_close = next_pred

    # Create forecast dataframe
    future_dates = create_future_dates(
        rf_data_featured['Date'].iloc[-1], period)
    forecast_df = pd.DataFrame({
        'ds': future_dates,
        'yhat': future_predictions
    })

    # Calculate metrics
    rf_mse = mean_squared_error(y_test, y_pred_test)
    rf_rmse = np.sqrt(rf_mse)
    rf_mae = mean_absolute_error(y_test, y_pred_test)

    # Display results
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Test RMSE", f"${rf_rmse:.2f}")
        st.metric("Test MAE", f"${rf_mae:.2f}")
        st.subheader('Random Forest Forecast Data')
        st.write(forecast_df.tail())

    with col2:
        current_price = data['Close'].iloc[-1]
        future_price = forecast_df['yhat'].iloc[-1]
        total_return, annual_return = calculate_metrics(
            current_price, future_price, n_years)

        st.metric("Current Price", f"${current_price:.2f}")
        st.metric(f"Forecast Price ({n_years} years)", f"${future_price:.2f}")
        st.metric("Total Return", f"{total_return:.2f}%")
        st.metric("Annualized Return", f"{annual_return:.2f}%")

    # Plot Random Forest results
    fig = go.Figure()

    # Historical data
    fig.add_trace(go.Scatter(
        x=data['Date'],
        y=data['Close'],
        name='Historical Data',
        line=dict(color='blue')
    ))

    # Test predictions
    fig.add_trace(go.Scatter(
        x=dates_test,
        y=y_pred_test,
        name='RF Test Predictions',
        line=dict(color='green')
    ))

    # Future forecast
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'],
        y=forecast_df['yhat'],
        name='RF Future Forecast',
        line=dict(color='orange', dash='dash')
    ))

    fig.update_layout(
        title=f'Random Forest Forecast - {selected_name}',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        xaxis_rangeslider_visible=True
    )

    st.plotly_chart(fig)

    # Feature importance
    with st.expander("Feature Importance"):
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)

        fig_importance = go.Figure(go.Bar(
            x=feature_importance['importance'][:10],
            y=feature_importance['feature'][:10],
            orientation='h'
        ))
        fig_importance.update_layout(
            title='Top 10 Feature Importance',
            xaxis_title='Importance',
            yaxis_title='Features'
        )
        st.plotly_chart(fig_importance)
