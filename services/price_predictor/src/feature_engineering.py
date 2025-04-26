import pandas as pd
import talib
from typing import Optional

def add_features(
        X: pd.DataFrame,
        rsi_timeperiod: Optional[int] = 14,
        momentum_timeperiod: Optional[int] = 14, 
        volatility_timeperiod: Optional[int] = 5,
)-> pd.DataFrame:
    """
    adds features to the dataframe
    :param X: dataframe with the OHLC data
    :param rsi_timeperiod: time period for the RSI indicator
    :param momentum_timeperiod: time period for the momentum indicator
    :param volatility_timeperiod: time period for the volatility indicator
    args:
        X: dataframe with the OHLC data
        rsi_timeperiod: time period for the RSI indicator
        momentum_timeperiod: time period for the momentum indicator
        volatility_timeperiod: time period for the volatility indicator
    returns:
        X: dataframe with the features added
    
    """
    X_ = add_momentum_indicators(X, rsi_timeperiod, momentum_timeperiod)
    X_ = add_volatility_indicators(X_, timeperiod=volatility_timeperiod)

    return X_



def add_momentum_indicators(
        x: pd.DataFrame,
        rsi_timeperiod: int = 14,
        momentum_timeperiod: int = 14,
                            
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

    return X_

def add_volatility_indicators(
        X: pd.DataFrame,
        timeperiod: Optional[int] = 5,
        nbdev: Optional[int] = 1,
)-> pd.DataFrame:
    """
    adds volatility indicators to the dataframe
    """
    X_ = X.copy()
    X_['std'] = talib.STDDEV(X_['close'], timeperiod=timeperiod, nbdev=nbdev)
    
    return X_