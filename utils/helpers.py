import plotly.graph_objects as go
import pandas as pd
from datetime import timedelta


def plot_raw_data(data):
    """Plot raw cryptocurrency data"""
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

    return fig


def create_future_dates(last_date, periods):
    """Create future dates for forecasting"""
    return pd.date_range(
        start=last_date + timedelta(days=1),
        periods=periods,
        freq='D'
    )


def calculate_metrics(current_price, future_price, n_years):
    """Calculate forecast metrics"""
    total_return = ((future_price / current_price) - 1) * 100
    annualized_return = ((future_price / current_price)
                         ** (1/n_years) - 1) * 100

    return total_return, annualized_return
