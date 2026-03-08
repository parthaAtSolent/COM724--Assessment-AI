import streamlit as st


def execute_forecasts(data, period, n_years, selected_name, selected_models, confidence_interval):
    """
    Execute selected forecasting models without retraining
    unless configuration changes.
    """

    if not selected_models:
        st.warning("⚠️ Please select at least one forecasting model.")
        return

    # Initialize session storage
    if "forecast_results" not in st.session_state:
        st.session_state.forecast_results = {}

    st.markdown("---")
    st.markdown("## 🔮 Price Forecasts")
    st.markdown(
        f"### Forecast Horizon: **{n_years} year{'s' if n_years > 1 else ''}**"
    )

    tabs = st.tabs([f"📈 {model}" for model in selected_models])

    for i, model_name in enumerate(selected_models):

        with tabs[i]:

            st.markdown(f"### {model_name} Forecast")

            # 🔑 Create unique config key
            model_key = f"{model_name}_{selected_name}_{n_years}_{confidence_interval}"

            # ✅ Train ONLY if this exact configuration not seen before
            if model_key not in st.session_state.forecast_results:

                with st.spinner(f"Training {model_name} model..."):

                    try:
                        if model_name == "Prophet":
                            from models.prophet_forecast import prophet_forecast
                            result = prophet_forecast(
                                data, period, n_years, selected_name
                            )

                        elif model_name == "ARIMA":
                            from models.arima_forecast import arima_forecast
                            result = arima_forecast(
                                data, period, n_years, selected_name
                            )

                        elif model_name == "LSTM":
                            from models.lstm_forecast import lstm_forecast
                            result = lstm_forecast(
                                data, period, n_years, selected_name
                            )

                        elif model_name == "Random Forest":
                            from models.random_forest_forecast import random_forest_forecast
                            result = random_forest_forecast(
                                data, period, n_years, selected_name, confidence_interval
                            )

                        st.session_state.forecast_results[model_key] = result

                    except Exception as e:
                        st.error(f"Error executing {model_name}: {str(e)}")
                        return

            # ✅ Display stored result (no retraining)
            result = st.session_state.forecast_results[model_key]

            if isinstance(result, dict):

                if "figure" in result:
                    st.plotly_chart(result["figure"], use_container_width=True)

                if "data" in result:
                    st.dataframe(result["data"], use_container_width=True)
