import pandas as pd


def interpolate_missing_candles(
    ohlc_data: pd.DataFrame,
    ohlc_window_sec: int,
) -> pd.DataFrame:
    """
    Interpolates missing candles in the OHLC data.

    Args:
        ohlc_data (pd.DataFrame): The OHLC data.
        ohlc_window_sec (int): The size of the window in seconds.

    Returns:
        pd.DataFrame: The OHLC data with the missing candles interpolated.
    """
    # Python trick!
    # We use inplace to avoid copying the data, which should be more efficient
    ohlc_data.set_index('timestamp', inplace=True)


    # complete list of timestamps for which we need to have rows in our dataframe
    from_ms = int(ohlc_data.index.min())
    to_ms = int(ohlc_data.index.max())
    labels = range(from_ms, to_ms, ohlc_window_sec * 1000)
    # reindex the dataframe to add missing rows
    ohlc_data = ohlc_data.reindex(labels)

    # interpolate missing values using forward fill for close prices
    ohlc_data['close'].ffill(inplace=True)

    # if ohlc_data['open] is null use the ohlc_data['close'] value
    ohlc_data['open'].fillna(ohlc_data['close'], inplace=True)
    # do the same for high and low
    ohlc_data['high'].fillna(ohlc_data['close'], inplace=True)
    ohlc_data['low'].fillna(ohlc_data['close'], inplace=True)

    # we have to forward fill the product_id as well
    ohlc_data['product_id'].ffill(inplace=True)

    # reset the index
    ohlc_data.reset_index(inplace=True)

    # let's make sure we have no missing datetimes
    ohlc_data['datetime'] = pd.to_datetime(ohlc_data['timestamp'], unit='ms')

    return ohlc_data