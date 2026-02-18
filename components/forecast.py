import streamlit as st
import plotly.graph_objects as go


def execute_forecasts(data, period, n_years, selected_name, selected_models, confidence_interval):
    """
    Execute selected forecasting models and display results
    """
    if not selected_models:
        st.warning(
            "⚠️ Please select at least one forecasting model from the sidebar.")
        return

    st.markdown("---")
    st.markdown("## 🔮 Price Forecasts")
    st.markdown(
        f"### Forecast Horizon: **{n_years} year{'s' if n_years > 1 else ''}**")

    # Create tabs for different models
    tabs = st.tabs([f"📈 {model}" for model in selected_models])
    results = {}

    # Execute each model in its own tab
    for i, model_name in enumerate(selected_models):
        with tabs[i]:
            st.markdown(f"### {model_name} Forecast")

            try:
                if model_name == "Prophet":
                    from models.prophet_forecast import prophet_forecast
                    forecast_result = prophet_forecast(
                        data, period, n_years, selected_name
                    )
                    results["Prophet"] = forecast_result

                elif model_name == "ARIMA":
                    from models.arima_forecast import arima_forecast
                    forecast_result = arima_forecast(
                        data, period, n_years, selected_name
                    )
                    results["ARIMA"] = forecast_result

                elif model_name == "LSTM":
                    from models.lstm_forecast import lstm_forecast
                    forecast_result = lstm_forecast(
                        data, period, n_years, selected_name
                    )
                    results["LSTM"] = forecast_result

                elif model_name == "Random Forest":
                    from models.random_forest_forecast import random_forest_forecast
                    forecast_result = random_forest_forecast(
                        data, period, n_years, selected_name, confidence_interval
                    )
                    results["Random Forest"] = forecast_result

            except Exception as e:
                st.error(f"Error executing {model_name} model: {str(e)}")
                st.info("Try selecting a different model or adjusting parameters.")
