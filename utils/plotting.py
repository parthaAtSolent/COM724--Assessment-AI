import plotly.graph_objs as go


def plot_time_series(data, title="Price over Time"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['Date'], y=data['Open'], name='Open', line=dict(color='blue')))
    fig.add_trace(go.Scatter(
        x=data['Date'], y=data['Close'], name='Close', line=dict(color='red')))
    fig.update_layout(title=title, xaxis_title='Date',
                      yaxis_title='Price (USD)', xaxis_rangeslider_visible=True)
    return fig
