from tools.ohlc_data_reader import OhlcDataReader
from src.data_preprocessing import create_target_metric, interpolate_missing_candles
import pandas as pd
from typing import Tuple
from loguru import logger


def train(
        product_id                     : str,
        ohlc_window_sec                : int,
        feature_view_name              : str,
        feature_view_version           : int,
        prediction_window_sec          : int,
        last_n_days_to_test_model      : int,
        last_n_days_to_fetch_from_store: int,
):
    """
    This function trains the model by following these steps

    1. Fetch OHLC data from the feature store
    2. Split the data into training and testing
    3. Preprocess the data. In this case we need missing value imputation.
    4. Create the target metric as a new column in our dataframe. This is what we want to predict.
    5. Train the model

    Args:
        product_id (str): The product ID to fetch data for.
        ohlc_window_sec (int): The OHLC window size in seconds.
        feature_view_name (str): The name of the feature view to use.
        feature_view_version (int): The version of the feature view to use.
        last_n_days_to_fetch_from_store (int): The number of days to fetch from the store.
        last_n_days_to_test (int): The number of days to test.
    returns:
        None
    """


# step 1:

    # Fetch OHLC data from the feature store
    ohlc_data_reader = OhlcDataReader(
                    ohlc_window_sec=ohlc_window_sec,
                    feature_view_name=feature_view_name,
                    feature_view_version=feature_view_version,
                        
    )
    # Read the OHLC data from the feature store
    logger.info(f"Fetching OHLC data for product {product_id} from the feature store")
    ohlc_data = ohlc_data_reader.read_from_offline_store(
                            product_id=product_id,
                            last_n_days=last_n_days_to_fetch_from_store,
    )
    # add the human readable datetime column
    ohlc_data['datetime'] = pd.to_datetime(ohlc_data['timestamp'], unit='ms')
    # breakpoint()

# step 2:

    # Split the data into training and testing using a cuttoff date
    logger.info('Splitting the data into training and testing')
    ohlc_train, ohlc_test = split_train_test(
        ohlc_data=ohlc_data,
        last_n_days_to_test_model=last_n_days_to_test_model,
    )

# step 3:

    #  Preprocess the data
    # Interpolate missing candles
    # interpolate function from the data_preprocessing module in src
    logger.info('Interpolating missing candles for training data')
    ohlc_train = interpolate_missing_candles(
        ohlc_train,ohlc_window_sec)
    logger.info('Interpolating missing candles for testing data')
    ohlc_test = interpolate_missing_candles(ohlc_test,ohlc_window_sec)
#step  4: 
    # Create the target metric as a new column in our dataframe for training and testing
    logger.info('Creating the target metric')
    ohlc_train = create_target_metric(
        ohlc_train,
        ohlc_window_sec,
        prediction_window_sec,
    )
    ohlc_test = create_target_metric(
        ohlc_test,
        ohlc_window_sec,
        prediction_window_sec,
    )

    # split the data into training and testing using a cuttoff date 

#--> part of step 2
    # this function is used to split the data into training and testing using a cuttoff date

def split_train_test(
    ohlc_data: pd.DataFrame, last_n_days_to_test_model: int
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits the data into training and testing using a cutoff date.

    Args:
        ohlc_data (pd.DataFrame): The OHLC data.
        last_n_days_to_test_model (int): The number of days to use for testing the model.

    Returns:
        pd.DataFrame: The training data.
        pd.DataFrame: The testing data.
    """
    # calculate the cutoff date
    cutoff_date = ohlc_data['datetime'].max() - pd.Timedelta(
        days=last_n_days_to_test_model
    )

    # split the data into training and testing
    ohlc_train = ohlc_data[ohlc_data['datetime'] < cutoff_date]
    ohlc_test = ohlc_data[ohlc_data['datetime'] >= cutoff_date]
    return ohlc_train, ohlc_test

    #breakpoint()


if __name__ == "__main__":
    train(
        product_id="BTC/USD",
        ohlc_window_sec=60,
        feature_view_name='ohlc_feature_view',
        feature_view_version=1,
        last_n_days_to_fetch_from_store=150,
        last_n_days_to_test_model=7,
        prediction_window_sec=60 * 5,
    )