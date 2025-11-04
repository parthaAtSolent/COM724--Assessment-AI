import streamlit as st
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import plotly.graph_objects as go
from utils.config import LSTM_SEQUENCE_LENGTH, LSTM_PARAMS, TRAIN_TEST_SPLIT
from utils.helpers import create_future_dates, calculate_metrics


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


def lstm_forecast(data, period, n_years, selected_name):
    """LSTM forecasting implementation"""
    st.subheader('LSTM Forecast')

    # Prepare data for LSTM
    lstm_data = data[['Close']].values

    # Normalize the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(lstm_data)

    # Create sequences
    with st.spinner('Preparing data for LSTM...'):
        X, y = create_sequences(scaled_data, LSTM_SEQUENCE_LENGTH)

        # Split data
        train_size = int(len(X) * TRAIN_TEST_SPLIT)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        # Reshape for LSTM
        X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
        X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

    # Create and train LSTM model
    with st.spinner('Training LSTM model...'):
        model = create_lstm_model(LSTM_SEQUENCE_LENGTH)

        # Train the model
        history = model.fit(
            X_train, y_train,
            epochs=LSTM_PARAMS['epochs'],
            batch_size=LSTM_PARAMS['batch_size'],
            validation_data=(X_test, y_test),
            verbose=LSTM_PARAMS['verbose'],
            shuffle=False
        )

    # Make predictions on test data
    test_predict = model.predict(X_test)
    test_predict = scaler.inverse_transform(test_predict)
    y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))

    # Forecast future values
    with st.spinner('Generating future forecasts...'):
        future_predictions = []

        # Start with the last sequence from training data
        current_sequence = scaled_data[-LSTM_SEQUENCE_LENGTH:].reshape(
            1, LSTM_SEQUENCE_LENGTH, 1)

        for _ in range(period):
            # Predict next value
            next_pred = model.predict(current_sequence, verbose=0)
            future_predictions.append(next_pred[0, 0])

            # Update sequence
            current_sequence = np.append(current_sequence[:, 1:, :],
                                         next_pred.reshape(1, 1, 1), axis=1)

    # Inverse transform future predictions
    future_predictions = scaler.inverse_transform(
        np.array(future_predictions).reshape(-1, 1))

    # Create forecast dataframe
    future_dates = create_future_dates(data['Date'].iloc[-1], period)
    forecast_df = pd.DataFrame({
        'ds': future_dates,
        'yhat': future_predictions.flatten()
    })

    # Calculate metrics
    mse = mean_squared_error(y_test_actual, test_predict)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test_actual, test_predict)

    # Display results
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Test RMSE", f"${rmse:.2f}")
        st.metric("Test MAE", f"${mae:.2f}")
        st.subheader('LSTM Forecast Data')
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

    # Plot LSTM results
    fig = go.Figure()

    # Historical data
    fig.add_trace(go.Scatter(
        x=data['Date'],
        y=data['Close'],
        name='Historical Data',
        line=dict(color='blue')
    ))

    # Test predictions
    test_dates = data['Date'].iloc[train_size +
                                   LSTM_SEQUENCE_LENGTH:].reset_index(drop=True)
    fig.add_trace(go.Scatter(
        x=test_dates,
        y=test_predict.flatten(),
        name='LSTM Test Predictions',
        line=dict(color='green')
    ))

    # Future forecast
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'],
        y=forecast_df['yhat'],
        name='LSTM Future Forecast',
        line=dict(color='red', dash='dash')
    ))

    fig.update_layout(
        title=f'LSTM Forecast - {selected_name}',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        xaxis_rangeslider_visible=True
    )

    st.plotly_chart(fig)

    # Plot training history
    with st.expander("Training History"):
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
