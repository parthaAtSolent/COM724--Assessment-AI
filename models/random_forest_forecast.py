import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.feature_selection import SelectFromModel
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.helpers import create_future_dates, calculate_metrics
import warnings
warnings.filterwarnings('ignore')


# =====================================================
# MODELS
# =====================================================

@st.cache_resource
def create_random_forest_model(
    n_estimators=100,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features="sqrt"
):
    return RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        max_features=max_features,
        random_state=42,
        n_jobs=-1
    )


@st.cache_resource
def create_gradient_boosting_model():
    return GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=3,
        random_state=42
    )


# =====================================================
# FEATURE ENGINEERING
# =====================================================

def prepare_features_for_rf(data, use_all_features=True):
    df = data[['Close']].copy()

    if use_all_features:
        exclude_cols = ['Target', 'Target_Change', 'Target_Binary']
        for col in data.columns:
            if col not in exclude_cols and col != 'Close':
                if data[col].notna().sum() > len(data) * 0.5:
                    df[col] = data[col]

    return df.fillna(method="ffill").fillna(method="bfill")


def create_interaction_features(df):
    interaction_features = {}

    if 'Volume' in df.columns:
        df['Volume_Close_Interaction'] = df['Volume'] * df['Close']
        interaction_features['Volume_Close_Interaction'] = 'Volume * Close'

    ma_features = [c for c in df.columns if c.startswith("MA_")]
    for ma in ma_features:
        df[f"{ma}_Premium"] = (df['Close'] - df[ma]) / (df[ma] + 1e-9)
        interaction_features[f"{ma}_Premium"] = f"(Close - {ma}) / {ma}"

    return df, interaction_features


# =====================================================
# MAIN ENTRY
# =====================================================

def random_forest_forecast(data, period, n_years, selected_name):
    st.subheader("🌲 Random Forest Forecasting")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌳 Standard RF",
        "🎯 Feature-Enhanced RF",
        "⚡ Ensemble Methods",
        "📊 Feature Analysis"
    ])

    with tab1:
        _rf_standard(data, period, n_years, selected_name)

    with tab2:
        _rf_enhanced(data, period, n_years, selected_name)

    with tab3:
        _rf_ensemble(data, period, n_years, selected_name)

    with tab4:
        _rf_feature_analysis(data, selected_name)


# =====================================================
# ✅ FIXED STANDARD RF (MAIN ISSUE)
# =====================================================

def _rf_standard(data, period, n_years, selected_name):
    st.markdown("### Standard Random Forest")

    df = prepare_features_for_rf(data, use_all_features=True)

    X = df.drop("Close", axis=1).fillna(0)
    y = df["Close"]
    dates = df.index

    train_size = int(len(X) * 0.8)

    X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
    y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

    train_dates = dates[:train_size]
    test_dates = dates[train_size:]

    rf = create_random_forest_model(n_estimators=100, max_depth=10)
    rf.fit(X_train, y_train)

    train_pred = rf.predict(X_train)
    test_pred = rf.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, test_pred))
    mae = mean_absolute_error(y_test, test_pred)
    r2 = r2_score(y_test, test_pred)

    col1, col2, col3 = st.columns(3)
    col1.metric("RMSE", f"{rmse:.2f}")
    col2.metric("MAE", f"{mae:.2f}")
    col3.metric("R²", f"{r2:.3f}")

    # ------------------------
    # FUTURE FORECAST
    # ------------------------
    last_features = X.iloc[-1:].copy()
    future_preds = []

    for _ in range(period):
        pred = rf.predict(last_features)[0]
        future_preds.append(pred)

        next_features = last_features.copy()
        for col in next_features.columns:
            if "lag_1" in col.lower():
                next_features[col] = pred

        last_features = next_features

    future_dates = create_future_dates(dates[-1], period)

    # ------------------------
    # PLOT (CLEAN + ALIGNED)
    # ------------------------
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=train_dates,
        y=y_train,
        name="Train (Historical)",
        line=dict(width=2)
    ))

    fig.add_trace(go.Scatter(
        x=test_dates,
        y=test_pred,
        name="Test Prediction",
        line=dict(dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=future_dates,
        y=future_preds,
        name="RF Forecast",
        line=dict(width=3, dash="dot")
    ))

    fig.update_layout(
        title=f"{selected_name} – Random Forest Forecast",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    current_price = y.iloc[-1]
    future_price = future_preds[-1]

    total_return, annual_return = calculate_metrics(
        current_price, future_price, n_years
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Price", f"${current_price:.2f}")
    col2.metric(f"{n_years}Y Forecast", f"${future_price:.2f}")
    col3.metric("Annual Return", f"{annual_return:.2f}%")


# =====================================================
# OTHER SECTIONS (UNCHANGED)
# =====================================================

def _rf_enhanced(data, period, n_years, selected_name):
    df = prepare_features_for_rf(data, use_all_features=True)
    df, _ = create_interaction_features(df)

    X = df.drop("Close", axis=1).fillna(0)
    y = df["Close"]

    selector = SelectFromModel(
        RandomForestRegressor(n_estimators=50, random_state=42),
        threshold="median"
    )
    selector.fit(X, y)
    X = X[X.columns[selector.get_support()]]

    split = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    model = create_random_forest_model(n_estimators=150, max_depth=15)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)

    st.metric("Enhanced RMSE", f"{rmse:.2f}")
    st.metric("Enhanced R²", f"{r2:.3f}")


def _rf_ensemble(data, period, n_years, selected_name):
    df = prepare_features_for_rf(data, True)
    X = df.drop("Close", axis=1).fillna(0)
    y = df["Close"]

    split = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    rf = create_random_forest_model()
    gb = create_gradient_boosting_model()

    rf.fit(X_train, y_train)
    gb.fit(X_train, y_train)

    results = pd.DataFrame([
        {"Model": "Random Forest", "RMSE": np.sqrt(
            mean_squared_error(y_test, rf.predict(X_test)))},
        {"Model": "Gradient Boosting", "RMSE": np.sqrt(
            mean_squared_error(y_test, gb.predict(X_test)))}
    ])

    st.dataframe(results)


def _rf_feature_analysis(data, selected_name):
    df = prepare_features_for_rf(data, True)
    X = df.drop("Close", axis=1).fillna(0)
    y = df["Close"]

    model = create_random_forest_model()
    model.fit(X, y)

    imp = pd.DataFrame({
        "Feature": X.columns,
        "Importance": model.feature_importances_
    }).sort_values("Importance", ascending=False)

    fig = go.Figure(go.Bar(
        x=imp["Importance"].head(20),
        y=imp["Feature"].head(20),
        orientation="h"
    ))

    fig.update_layout(title="Top Feature Importance", height=500)
    st.plotly_chart(fig, use_container_width=True)
