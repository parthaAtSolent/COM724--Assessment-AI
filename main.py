from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.layers import Dense, LSTM, Dropout  # type: ignore
from tensorflow.keras.models import Sequential  # type: ignore

import warnings
from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
import streamlit as st
from datetime import date, timedelta

import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go

import pandas as pd
import numpy as np

START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

st.title('Cryptocurrency Forecast App')

cryptos = {
    'BTC-USD': 'Bitcoin',
    'ETH-USD': 'Ethereum',
    'BNB-USD': 'Binance Coin',
    'XRP-USD': 'Ripple',
    'SOL-USD': 'Solana',
    'ADA-USD': 'Cardano',
    'DOGE-USD': 'Dogecoin',
    'DOT-USD': 'Polkadot',
    'AVAX-USD': 'Avalanche',
    'MATIC-USD': 'Polygon',
    'SHIB-USD': 'Shiba Inu',
    'LTC-USD': 'Litecoin',
    'TRX-USD': 'TRON',
    'BCH-USD': 'Bitcoin Cash',
    'ATOM-USD': 'Cosmos',
    'LINK-USD': 'Chainlink',
    'XLM-USD': 'Stellar',
    'UNI-USD': 'Uniswap',
    'XMR-USD': 'Monero',
    'ETC-USD': 'Ethereum Classic',
    'NEAR-USD': 'NEAR Protocol',
    'VET-USD': 'VeChain',
    'ICP-USD': 'Internet Computer',
    'FIL-USD': 'Filecoin',
    'EOS-USD': 'EOS',
    'APT-USD': 'Aptos',
    'SAND-USD': 'The Sandbox',
    'AAVE-USD': 'Aave',
    'MANA-USD': 'Decentraland',
    'THETA-USD': 'Theta Network',
    'EGLD-USD': 'MultiversX (Elrond)'
}

selected_name = st.selectbox(
    'Select cryptocurrency for prediction',
    list(cryptos.values())
)
# Get the symbol corresponding to the selected name
selected_crypto = [k for k, v in cryptos.items() if v == selected_name][0]

n_years = st.slider('Years of prediction:', 1, 4)
period = n_years * 365


@st.cache_data
def load_data(ticker):
    data = yf.download(ticker, START, TODAY)
    data.reset_index(inplace=True)

    # Flatten column names if they are multi-indexed
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]

    return data


data_load_state = st.text('Loading data...')
data = load_data(selected_crypto)
data_load_state.text('Loading data... done!')

st.subheader('Raw data')
st.write(data.tail())


def plot_raw_data():
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data['Date'],
        y=data['Open'],
        name="crypto_open",
        line=dict(color='blue')
    ))

    fig.add_trace(go.Scatter(
        x=data['Date'],
        y=data['Close'],
        name="crypto_close",
        line=dict(color='red')
    ))

    fig.update_layout(
        title_text='Time Series Data with Rangeslider',
        xaxis_rangeslider_visible=True,
        xaxis_title='Date',
        yaxis_title='Price (USD)'
    )

    st.plotly_chart(fig)


plot_raw_data()


# Predict forecast with Prophet.

st.subheader('Prophet Forecast')

df_train = data[['Date', 'Close']]
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

m = Prophet()
m.fit(df_train)
future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)

# Show and plot forecast
st.subheader('Forecast data')
st.write(forecast.tail())

st.write(f'Forecast plot for {n_years} years')
fig1 = plot_plotly(m, forecast)
st.plotly_chart(fig1)

st.write("Forecast components")
fig2 = m.plot_components(forecast)

st.pyplot(fig2)


# ARIMA Forecasting
warnings.filterwarnings('ignore')

st.subheader('ARIMA Forecast')

# Prepare data for ARIMA
df_arima = data[['Date', 'Close']].set_index('Date')

# Split data for training
train_size = int(len(df_arima) * 0.8)
train_data = df_arima.iloc[:train_size]
test_data = df_arima.iloc[train_size:]

with st.spinner('Finding best ARIMA model...'):
    # Auto ARIMA to find best parameters
    auto_model = auto_arima(
        train_data['Close'],
        seasonal=False,
        trace=False,
        error_action='ignore',
        suppress_warnings=True,
        stepwise=True
    )

    st.write(f"Best ARIMA model: {auto_model}")

# Fit the model on entire dataset
final_model = ARIMA(df_arima['Close'], order=auto_model.order)
fitted_model = final_model.fit()

# Forecast future values
forecast_periods = n_years * 365
forecast_result = fitted_model.get_forecast(steps=forecast_periods)
forecast_values = forecast_result.predicted_mean
conf_int = forecast_result.conf_int()

# Create future dates
last_date = df_arima.index[-1]
future_dates = pd.date_range(
    start=last_date + timedelta(days=1),
    periods=forecast_periods,
    freq='D'
)

# Create forecast dataframe
forecast_df = pd.DataFrame({
    'ds': future_dates,
    'yhat': forecast_values,
    'yhat_lower': conf_int.iloc[:, 0],
    'yhat_upper': conf_int.iloc[:, 1]
})

# Show forecast data
st.subheader('ARIMA Forecast data')
st.write(forecast_df.tail())

# Plot ARIMA forecast
st.write(f'ARIMA Forecast plot for {n_years} years')

fig_arima = go.Figure()

# Historical data
fig_arima.add_trace(go.Scatter(
    x=df_arima.index,
    y=df_arima['Close'],
    name='Historical Data',
    line=dict(color='blue')
))

# Forecast
fig_arima.add_trace(go.Scatter(
    x=forecast_df['ds'],
    y=forecast_df['yhat'],
    name='ARIMA Forecast',
    line=dict(color='red', dash='dash')
))

# Confidence interval
fig_arima.add_trace(go.Scatter(
    x=forecast_df['ds'].tolist() + forecast_df['ds'].tolist()[::-1],
    y=forecast_df['yhat_upper'].tolist(
    ) + forecast_df['yhat_lower'].tolist()[::-1],
    fill='toself',
    fillcolor='rgba(255,0,0,0.2)',
    line=dict(color='rgba(255,255,255,0)'),
    name='95% Confidence Interval'
))

fig_arima.update_layout(
    title=f'ARIMA Forecast - {selected_name}',
    xaxis_title='Date',
    yaxis_title='Price (USD)',
    xaxis_rangeslider_visible=True
)

st.plotly_chart(fig_arima)

# Model summary
st.subheader('ARIMA Model Summary')
st.text(str(fitted_model.summary()))

# Forecast statistics
current_price = df_arima['Close'].iloc[-1]
forecast_end_price = forecast_df['yhat'].iloc[-1]
total_return = ((forecast_end_price / current_price) - 1) * 100

st.subheader('Forecast Statistics')
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Current Price", f"${current_price:.2f}")
with col2:
    st.metric(f"Forecast in {n_years} years", f"${forecast_end_price:.2f}")
with col3:
    st.metric("Total Return", f"{total_return:.2f}%")


# LSTM Forecasting

st.subheader('LSTM Forecast')


@st.cache_resource
def create_lstm_model(sequence_length):
    """Create and compile LSTM model"""
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(sequence_length, 1)),
        Dropout(0.2),
        LSTM(50, return_sequences=True),
        Dropout(0.2),
        LSTM(50),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


def create_sequences(data, sequence_length):
    """Create sequences for LSTM training"""
    X, y = [], []
    for i in range(sequence_length, len(data)):
        X.append(data[i-sequence_length:i, 0])
        y.append(data[i, 0])
    return np.array(X), np.array(y)


# Prepare data for LSTM
lstm_data = data[['Close']].values

# Normalize the data
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(lstm_data)

# Set parameters
sequence_length = 60
train_size = int(len(scaled_data) * 0.8)

# Create sequences
with st.spinner('Preparing data for LSTM...'):
    X, y = create_sequences(scaled_data, sequence_length)

    # Split data
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # Reshape for LSTM
    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

# Create and train LSTM model
with st.spinner('Training LSTM model...'):
    model = create_lstm_model(sequence_length)

    # Train the model
    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_data=(X_test, y_test),
        verbose=0,
        shuffle=False
    )

# Make predictions on test data
test_predict = model.predict(X_test)
test_predict = scaler.inverse_transform(test_predict)
y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))

# Forecast future values
with st.spinner('Generating future forecasts...'):
    future_periods = n_years * 365
    future_predictions = []

    # Start with the last sequence from training data
    current_sequence = scaled_data[-sequence_length:].reshape(
        1, sequence_length, 1)

    for _ in range(future_periods):
        # Predict next value
        next_pred = model.predict(current_sequence, verbose=0)
        future_predictions.append(next_pred[0, 0])

        # Update sequence
        current_sequence = np.append(current_sequence[:, 1:, :],
                                     next_pred.reshape(1, 1, 1), axis=1)

# Inverse transform future predictions
future_predictions = scaler.inverse_transform(
    np.array(future_predictions).reshape(-1, 1)
)

# Create future dates
last_date = data['Date'].iloc[-1]
future_dates = pd.date_range(
    start=last_date + timedelta(days=1),
    periods=future_periods,
    freq='D'
)

# Create forecast dataframe
forecast_df_lstm = pd.DataFrame({
    'ds': future_dates,
    'yhat': future_predictions.flatten()
})

# Plot LSTM results
fig_lstm = go.Figure()

# Historical data
fig_lstm.add_trace(go.Scatter(
    x=data['Date'],
    y=data['Close'],
    name='Historical Data',
    line=dict(color='blue')
))

# Test predictions
test_dates = data['Date'].iloc[train_size +
                               sequence_length:].reset_index(drop=True)
fig_lstm.add_trace(go.Scatter(
    x=test_dates,
    y=test_predict.flatten(),
    name='LSTM Test Predictions',
    line=dict(color='green')
))

# Future forecast
fig_lstm.add_trace(go.Scatter(
    x=forecast_df_lstm['ds'],
    y=forecast_df_lstm['yhat'],
    name='LSTM Future Forecast',
    line=dict(color='red', dash='dash')
))

fig_lstm.update_layout(
    title=f'LSTM Forecast - {selected_name}',
    xaxis_title='Date',
    yaxis_title='Price (USD)',
    xaxis_rangeslider_visible=True
)

st.plotly_chart(fig_lstm)

# Calculate metrics
mse = mean_squared_error(y_test_actual, test_predict)
rmse = np.sqrt(mse)

# Display metrics and forecast data
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Test RMSE", f"${rmse:.2f}")
with col2:
    current_price = data['Close'].iloc[-1]
    st.metric("Current Price", f"${current_price:.2f}")
with col3:
    future_price = forecast_df_lstm['yhat'].iloc[-1]
    st.metric(f"Forecast in {n_years} years", f"${future_price:.2f}")

# Show forecast data
st.subheader('LSTM Forecast Data')
st.write(forecast_df_lstm.tail())

# Plot training history
st.subheader('LSTM Training History')
fig_loss = go.Figure()
fig_loss.add_trace(go.Scatter(
    y=history.history['loss'],
    name='Training Loss',
    line=dict(color='blue')
))
fig_loss.add_trace(go.Scatter(
    y=history.history['val_loss'],
    name='Validation Loss',
    line=dict(color='red')
))
fig_loss.update_layout(
    title='Model Training Loss',
    xaxis_title='Epoch',
    yaxis_title='Loss'
)
st.plotly_chart(fig_loss)

# Add this after your existing imports
# Random Forest Forecasting
st.subheader('Random Forest Forecast')


@st.cache_resource
def create_random_forest_model():
    """Create and return a Random Forest model"""
    return RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        max_depth=10,
        min_samples_split=5,
        n_jobs=-1
    )


def create_features(_data, lookback=60):
    """Create time series features using only Date and Close columns"""
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


# Prepare data for Random Forest
with st.spinner('Preparing data for Random Forest...'):
    rf_data = data[['Date', 'Close']].copy()
    rf_data['Date'] = pd.to_datetime(rf_data['Date'])

    # Create features
    rf_data_featured = create_features(rf_data)

    # Drop rows with NaN values (from lag features)
    rf_data_featured = rf_data_featured.dropna()

    # Define features - exclude Date and Close
    feature_columns = [
        col for col in rf_data_featured.columns if col not in ['Date', 'Close']]
    X = rf_data_featured[feature_columns]
    y = rf_data_featured['Close']

    # Split data
    train_size = int(len(X) * 0.8)
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
    future_periods = n_years * 365
    future_predictions = []

    # Start with the last row of actual data
    current_features = rf_data_featured.iloc[-1][feature_columns].copy()
    last_date = rf_data_featured['Date'].iloc[-1]
    last_close = rf_data_featured['Close'].iloc[-1]

    # Store recent prices for lag features
    recent_prices = list(rf_data_featured['Close'].iloc[-60:])

    for i in range(future_periods):
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
        next_date = last_date + timedelta(days=i + 1)
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
        feature_df = pd.DataFrame([feature_dict])[feature_columns].fillna(0)

        # Make prediction
        next_pred = rf_model.predict(feature_df)[0]
        future_predictions.append(next_pred)

        # Update for next iteration
        recent_prices.append(next_pred)
        if len(recent_prices) > 60:
            recent_prices.pop(0)
        last_close = next_pred

# Create future dates
future_dates = pd.date_range(
    start=rf_data_featured['Date'].iloc[-1] + timedelta(days=1),
    periods=future_periods,
    freq='D'
)

# Create forecast dataframe
forecast_df_rf = pd.DataFrame({
    'ds': future_dates,
    'yhat': future_predictions
})

# Plot Random Forest results
fig_rf = go.Figure()

# Historical data
fig_rf.add_trace(go.Scatter(
    x=data['Date'],
    y=data['Close'],
    name='Historical Data',
    line=dict(color='blue')
))

# Test predictions
fig_rf.add_trace(go.Scatter(
    x=dates_test,
    y=y_pred_test,
    name='RF Test Predictions',
    line=dict(color='green')
))

# Future forecast
fig_rf.add_trace(go.Scatter(
    x=forecast_df_rf['ds'],
    y=forecast_df_rf['yhat'],
    name='RF Future Forecast',
    line=dict(color='orange', dash='dash')
))

fig_rf.update_layout(
    title=f'Random Forest Forecast - {selected_name}',
    xaxis_title='Date',
    yaxis_title='Price (USD)',
    xaxis_rangeslider_visible=True
)

st.plotly_chart(fig_rf)

# Calculate metrics
rf_mse = mean_squared_error(y_test, y_pred_test)
rf_rmse = np.sqrt(rf_mse)
rf_mae = mean_absolute_error(y_test, y_pred_test)

# Display metrics and forecast data
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Test RMSE", f"${rf_rmse:.2f}")
with col2:
    st.metric("Test MAE", f"${rf_mae:.2f}")
with col3:
    current_price = data['Close'].iloc[-1]
    st.metric("Current Price", f"${current_price:.2f}")
with col4:
    future_price = forecast_df_rf['yhat'].iloc[-1]
    st.metric(f"Forecast in {n_years} years", f"${future_price:.2f}")

# Show forecast data
st.subheader('Random Forest Forecast Data')
st.write(forecast_df_rf.tail())

# Feature importance
st.subheader('Feature Importance')
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
