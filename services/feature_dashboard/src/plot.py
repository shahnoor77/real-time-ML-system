import pandas as pd
from bokeh.plotting import figure #, Figure

from datetime import timedelta
from typing import Optional

def plot_candles(
    df: pd.DataFrame,
    window_seconds: Optional[int] = 60,
    title: Optional[str] = '',
) -> 'Figure':
    """Generates a candlestick plot using the provided data in `df_` and the
    Bokeh library

    Args:
        df_ (pd.DataFrame): columns
            - open
            - high
            - low
            - close

    Returns:
        figure.Figure: Bokeh figure with candlestick and Bollinger bands
    """
    # convert the timestamp column in unix seconds to a datetime object
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')

    inc = df.close > df.open
    dec = df.open > df.close
    w = 1000 * window_seconds / 2  # band width in ms

    TOOLS = 'pan,wheel_zoom,box_zoom,reset,save'

    # x_max = df["date"].max() + timedelta(minutes=1)
    # x_min = df["date"].max() - timedelta(minutes=last_minutes)
    x_max = df['date'].max() + timedelta(minutes=5)
    x_min = df['date'].min() - timedelta(minutes=5)
    p = figure(
        x_axis_type='datetime',
        tools=TOOLS,
        width=1000,
        title=title,
        x_range=(x_min, x_max),
    )
    p.grid.grid_line_alpha = 0.3

    p.segment(df.date, df.high, df.date, df.low, color='black')
    p.vbar(
        df.date[inc],
        w,
        df.open[inc],
        df.close[inc],
        fill_color='#70bd40',
        line_color='black',
    )
    p.vbar(
        df.date[dec],
        w,
        df.open[dec],
        df.close[dec],
        fill_color='#F2583E',
        line_color='black',
    )

    return p