import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
import warnings
import plotly.graph_objects as go
from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
from utils.helpers import create_future_dates, calculate_metrics


def arima_forecast(data, period, n_years, selected_name):
    """ARIMA forecasting implementation"""
    st.subheader('ARIMA Forecast')

    # Prepare data for ARIMA
    df_arima = data[['Date', 'Close']].set_index('Date')

    with st.spinner('Finding best ARIMA model...'):
        # Auto ARIMA to find best parameters
        auto_model = auto_arima(
            df_arima['Close'],
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
    forecast_result = fitted_model.get_forecast(steps=period)
    forecast_values = forecast_result.predicted_mean
    conf_int = forecast_result.conf_int()

    # Create forecast dataframe
    future_dates = create_future_dates(df_arima.index[-1], period)
    forecast_df = pd.DataFrame({
        'ds': future_dates,
        'yhat': forecast_values,
        'yhat_lower': conf_int.iloc[:, 0],
        'yhat_upper': conf_int.iloc[:, 1]
    })

    # Display results
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('ARIMA Forecast Data')
        st.write(forecast_df.tail())

    with col2:
        current_price = df_arima['Close'].iloc[-1]
        future_price = forecast_df['yhat'].iloc[-1]
        total_return, annual_return = calculate_metrics(
            current_price, future_price, n_years)

        st.metric("Current Price", f"${current_price:.2f}")
        st.metric(f"Forecast Price ({n_years} years)", f"${future_price:.2f}")
        st.metric("Total Return", f"{total_return:.2f}%")
        st.metric("Annualized Return", f"{annual_return:.2f}%")

    # Plot ARIMA forecast
    fig = go.Figure()

    # Historical data
    fig.add_trace(go.Scatter(
        x=df_arima.index,
        y=df_arima['Close'],
        name='Historical Data',
        line=dict(color='blue')
    ))

    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'],
        y=forecast_df['yhat'],
        name='ARIMA Forecast',
        line=dict(color='red', dash='dash')
    ))

    # Confidence interval
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'].tolist() + forecast_df['ds'].tolist()[::-1],
        y=forecast_df['yhat_upper'].tolist(
        ) + forecast_df['yhat_lower'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(255,0,0,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='95% Confidence Interval'
    ))

    fig.update_layout(
        title=f'ARIMA Forecast - {selected_name}',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        xaxis_rangeslider_visible=True
    )

    st.plotly_chart(fig)

    # Model summary
    with st.expander("ARIMA Model Summary"):
        st.text(str(fitted_model.summary()))
