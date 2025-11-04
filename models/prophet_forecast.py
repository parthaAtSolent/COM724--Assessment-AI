import streamlit as st
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly
from utils.helpers import create_future_dates, calculate_metrics


def prophet_forecast(data, period, n_years, selected_name):
    """Prophet forecasting implementation"""
    st.subheader('Prophet Forecast')

    # Prepare data for Prophet
    df_train = data[['Date', 'Close']]
    df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

    with st.spinner('Training Prophet model...'):
        m = Prophet()
        m.fit(df_train)
        future = m.make_future_dataframe(periods=period)
        forecast = m.predict(future)

    # Display results
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Forecast Data')
        st.write(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())

    with col2:
        current_price = data['Close'].iloc[-1]
        future_price = forecast['yhat'].iloc[-1]
        total_return, annual_return = calculate_metrics(
            current_price, future_price, n_years)

        st.metric("Current Price", f"${current_price:.2f}")
        st.metric(f"Forecast Price ({n_years} years)", f"${future_price:.2f}")
        st.metric("Total Return", f"{total_return:.2f}%")
        st.metric("Annualized Return", f"{annual_return:.2f}%")

    # Plot forecast
    st.write(f'Prophet Forecast for {n_years} years')
    fig1 = plot_plotly(m, forecast)
    st.plotly_chart(fig1)

    # Plot components
    st.write("Forecast Components")
    fig2 = m.plot_components(forecast)
    st.pyplot(fig2)
