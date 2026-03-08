import streamlit as st
import plotly.graph_objects as go


def execute_forecasts(data, period, n_years, selected_name, selected_models, confidence_interval):

    if not selected_models:
        st.warning("⚠️ Please select at least one forecasting model.")
        st.session_state.prev_selected_models = []
        return

    if "forecast_results" not in st.session_state:
        st.session_state.forecast_results = {}
    if "prev_selected_models" not in st.session_state:
        st.session_state.prev_selected_models = []

    prev = st.session_state.prev_selected_models
    newly_added = [m for m in selected_models if m not in prev]

    auto_focus_index = None
    if newly_added:
        new_model = newly_added[-1]
        auto_focus_index = selected_models.index(new_model)

    st.session_state.prev_selected_models = list(selected_models)

    if auto_focus_index is not None:
        st.components.v1.html(
            f"""
            <script>
                function switchTab() {{
                    const tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"]');
                    if (tabs.length > {auto_focus_index}) {{
                        tabs[{auto_focus_index}].click();
                    }} else {{
                        setTimeout(switchTab, 100);
                    }}
                }}
                setTimeout(switchTab, 150);
            </script>
            """,
            height=0,
        )

    st.markdown("## Price Forecasts")

    if selected_models:
        tabs = st.tabs([f"📈 {model}" for model in selected_models])

        for i, model_name in enumerate(selected_models):

            with tabs[i]:

                # NEW TITLE (replaces Forecast Horizon)
                st.markdown(
                    f"### {model_name} Forecast: **{selected_name} ({n_years} year{'s' if n_years > 1 else ''})**"
                )

                conf_str = f"{confidence_interval:.2f}"
                model_key = f"{model_name}_{selected_name}_{n_years}_{conf_str}"

                if model_key not in st.session_state.forecast_results:

                    with st.spinner(f"Training {model_name} model..."):

                        try:
                            if model_name == "Prophet":
                                from models.prophet_forecast import prophet_forecast
                                result = prophet_forecast(
                                    data, period, n_years, selected_name)

                            elif model_name == "ARIMA":
                                from models.arima_forecast import arima_forecast
                                result = arima_forecast(
                                    data, period, n_years, selected_name)

                            elif model_name == "LSTM":
                                from models.lstm_forecast import lstm_forecast
                                result = lstm_forecast(
                                    data, period, n_years, selected_name)

                            elif model_name == "Random Forest":
                                from models.random_forest_forecast import random_forest_forecast
                                result = random_forest_forecast(
                                    data, period, n_years, selected_name, confidence_interval)

                            st.session_state.forecast_results[model_key] = result

                        except Exception as e:
                            st.error(f"Error executing {model_name}: {str(e)}")
                            st.session_state.forecast_results[model_key] = {
                                "error": str(e)}
                            continue

                result = st.session_state.forecast_results.get(model_key)

                if result is None:
                    st.warning(f"No forecast data available for {model_name}")
                    continue

                if isinstance(result, dict) and "error" in result:
                    st.error(
                        f"Failed to generate {model_name} forecast: {result['error']}")
                    continue

                # Info
                if "info" in result:
                    st.info(result["info"])

                # ---- CHART FIRST ----
                if "figure" in result:
                    st.plotly_chart(result["figure"], use_container_width=True)

                # ---- METRICS MOVED BELOW ----
                if "metrics" in result:

                    metrics = result["metrics"]

                    st.markdown("### Model Performance")

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("RMSE", f"{metrics.get('rmse', 0):.2f}")

                    with col2:
                        st.metric("MAE", f"{metrics.get('mae', 0):.2f}")

                    with col3:
                        st.metric("R² Score", f"{metrics.get('r2', 0):.4f}")

                    with col4:
                        st.metric("MAPE", f"{metrics.get('mape', 0):.2f}%")
