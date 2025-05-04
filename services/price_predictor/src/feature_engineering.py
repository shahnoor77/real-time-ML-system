from typing import Optional

import pandas as pd
import talib


def add_features(
        X: pd.DataFrame,
        n_candles_into_future: int,
        rsi_timeperiod: Optional[int] = 14,
        momentum_timeperiod: Optional[int] = 14, 
        volatility_timeperiod: Optional[int] = 5,
        fillna: Optional[bool] = True,
)-> pd.DataFrame:
    """
        Adds the following features to the given DataFrame:
 
     - RSI indicator -> `rsi` column
     - Momentum indicator -> `momentum` column
     - Standard deviation -> `std` column
 
     - Last observed target -> `last_observed_target` column
     - Temporal features -> `day_of_week`, `hour_of_day`, `minute_of_hour` columns
 
     Args:
         - X: pd.DataFrame: the input DataFrame
         - n_candles_into_future: int: the number of candles into the future to predict
         - discretization_thresholds: list: the thresholds to discretize the target
         - rsi_timeperiod: int: the time period for the RSI indicator
         - momentum_timeperiod: int: the time period for the momentum indicator
         - volatility_timeperiod: int: the time period for the standard deviation    
 
     Returns:
         - pd.DataFrame: the input DataFrame with the new columns
    
    """
    
    X_ = add_momentum_indicators(X, rsi_timeperiod, momentum_timeperiod)
    X_ = add_volatility_indicators(X_, timeperiod=volatility_timeperiod)
    X_ = add_macd_indicator(X_, fillna=fillna)
    X_ = add_last_observed_target(
                X_,
                n_candles_into_future = n_candles_into_future,
                )
    X_ = add_temporal_features(X_)

    return X_


def add_macd_indicator(
    X: pd.DataFrame,
    fastperiod: Optional[int] = 12,
    slowperiod: Optional[int] = 26,
    signalperiod: Optional[int] = 9,
    fillna: Optional[bool] = True,
) -> pd.DataFrame:
    """
    Adds the MACD (Moving Average Convergence Divergence) indicator to the `ts_data`
    """
    X_ = X.copy()
 
    macd, macd_signal, _ = talib.MACD(
        X_['close'],
        fastperiod=fastperiod,
        slowperiod=slowperiod,
        signalperiod=signalperiod,
    )
    X_['MACD'] = macd
    X_['MACD_Signal'] = macd_signal
 
    if fillna:
        X_['MACD'] = X_['MACD'].fillna(0)
        X_['MACD_Signal'] = X_['MACD_Signal'].fillna(0)
         
    return X_

def add_temporal_features(
        x: pd.DataFrame,
)-> pd.DataFrame:
    """
    Adds columns with temporal features to the given DataFrame using the X['datetime']
     - day_of_week
     - hour_of_day
     - minute_of_hour
 
     Args:
         - X: pd.DataFrame: the input DataFrame
 
     Returns:
         - pd.DataFrame: the input DataFrame with the new columns
    """
    X_ = x.copy()
    X_['days_of_week'] = X_['datetime'].dt.dayofweek
    X_['hour_of_day'] = X_['datetime'].dt.hour
    X_['minute_of_hour'] = X_['datetime'].dt.minute

    return X_



def add_momentum_indicators(
        x: pd.DataFrame,
        rsi_timeperiod: int = 14,
        momentum_timeperiod: int = 14,
        fillna: Optional[bool] = True,
                            
    ) -> pd.DataFrame:
    """
    adds momentum indicators to the dataframe
    :param x: dataframe with the OHLC data
    :param rsi_timeperiod: time period for the RSI indicator
    :param momentum_timeperiod: time period for the momentum indicator
    args:
        x: dataframe with the OHLC data
        rsi_timeperiod: time period for the RSI indicator
        momentum_timeperiod: time period for the momentum indicator
    returns:
        x: dataframe with the momentum indicators added
    
    """
    X_ = x.copy()
    X_['rsi'] = talib.RSI(X_['close'], timeperiod=rsi_timeperiod)
    X_['momentum'] = talib.MOM(X_['close'], timeperiod=momentum_timeperiod)

    if fillna:
         X_['rsi'] = X_['rsi'].fillna(0)
         X_['momentum'] = X_['momentum'].fillna(0)

    return X_

def add_volatility_indicators(
        X: pd.DataFrame,
        timeperiod: Optional[int] = 5,
        nbdev: Optional[int] = 1,
        fillna: Optional[bool] = True,
)-> pd.DataFrame:
    """
    adds volatility indicators to the dataframe
    """
    X_ = X.copy()
    X_['std'] = talib.STDDEV(X_['close'], timeperiod=timeperiod, nbdev=nbdev)
    if fillna:
         X_['std'] = X_['std'].fillna(0)
    
    return X_



def add_last_observed_target(
    X: pd.DataFrame,
    n_candles_into_future: int,
    
) -> pd.DataFrame:
    """
     Adds the target column to the given DataFrame.
 
     Args:
         - X: pd.DataFrame: the input DataFrame
         - n_candles_into_future: int: the number of candles into the future to predict
         - discretization_thresholds: list: the thresholds to discretize the target
     
     Returns:
         - pd.DataFrame: the input DataFrame with the new column
    """
    X_ = X.copy()
 
    X_['last_observed_target'] = X_['close'] \
             .pct_change(n_candles_into_future)
    X_['last_observed_target'].fillna(0, inplace=True)
    return X_


     
    