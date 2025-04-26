
import pandas as pd
from loguru import logger
from typing import Tuple
 
from tools.ohlc_data_reader import OhlcDataReader
 
 
def train(
     feature_view_name: str,
     feature_view_version: int,
     ohlc_window_sec: int,
     product_id: str,
     last_n_days_to_fetch_from_store: int,
     last_n_days_to_test_model: int,
     discretization_thresholds: list,
     prediction_window_sec: int,
 ):
     """
     This function trains the model by following these steps
     
     1. Fetch OHLC data from the feature store
     2. Split the data into training and testing
     3. Preprocess the data. In this case we need missing value imputation.
     4. Create the target metric as a new column in our dataframe. This is what we want to predict.
     5. Train the model
 
     Args:
         feature_view_name (str): The name of the feature view in the feature store.
         feature_view_version (int): The version of the feature view in the feature store.
         ohlc_window_sec (int): The size of the window in seconds.
         product_id (str): The product id.
         last_n_days_to_fetch_from_store (int): The number of days to fetch from the feature store.
         last_n_days_to_test_model (int): The number of days to use for testing the model.
         discretization_thresholds (list): The thresholds to discretize the close price.
         prediction_window_sec (int): The size of the prediction window in seconds.
 
     Returns:
         Nothing.
         The model artifact is pushed to the model registry.
     """
     # Step 1    
     # Fetch the data from the feature store
     ohlc_data_reader = OhlcDataReader(
         ohlc_window_sec=ohlc_window_sec,
         feature_view_name=feature_view_name,
         feature_view_version=feature_view_version,
     )
     logger.info('Fetching OHLC data from the feature store')
     ohlc_data = ohlc_data_reader.read_from_offline_store(
         product_id=product_id,
         last_n_days=last_n_days_to_fetch_from_store,
     )
 
     # add a column to ohlc_data with a human-readable data, using
     # the ohlc_data['timestamp'] column in milliseconds
     ohlc_data['datetime'] = pd.to_datetime(ohlc_data['timestamp'], unit='ms')
 
     # Step 2
     # Split the data into training and testing using a cutoff date
     logger.info('Splitting the data into training and testing')
     ohlc_train, ohlc_test = split_train_test(
         ohlc_data=ohlc_data,
         last_n_days_to_test_model=last_n_days_to_test_model,
     )
 
     # Step 3
     # Preprocess the data for training and for testing
     # Interpolate missing candles
     logger.info('Interpolating missing candles for training data')
     ohlc_train = interpolate_missing_candles(ohlc_train, ohlc_window_sec)
     logger.info('Interpolating missing candles for testing data')
     ohlc_test = interpolate_missing_candles(ohlc_test, ohlc_window_sec)
 
     # Step 4
     # Create the target metric as a new column in our dataframe for training and testing
     logger.info('Creating the target metric')
     ohlc_train = create_target_metric(
         ohlc_train,
         ohlc_window_sec,
         discretization_thresholds,
         prediction_window_sec,
     )
     ohlc_test = create_target_metric(
         ohlc_test,
         ohlc_window_sec,
         discretization_thresholds,
         prediction_window_sec,
     )
 
     # Plot distribution of the target
     logger.info('Distribution of the target in the training data')
     logger.debug(ohlc_train['target'].value_counts())
     logger.info('Distribution of the target in the testing data')
     logger.debug(ohlc_test['target'].value_counts())
 
     # Before training, let's split the features and the target
     X_train = ohlc_train.drop(columns=['target'])
     y_train = ohlc_train['target']
     X_test = ohlc_test.drop(columns=['target'])
     y_test = ohlc_test['target']
     
     # Step 5
     # TODO: build a ML model that given the features in ohlc_train (aka all columns except 'target')
     # predicts the target (aka ohlc_train['target'])
     # Let's build a baseline model
     from src.baseline_model import BaselineModel
     model = BaselineModel(
         n_candles_into_future=prediction_window_sec // ohlc_window_sec,
         discretization_thresholds=discretization_thresholds,
     )
     y_test_predictions = model.predict(X_test)
 
     # Let's evaluate the model. It is a classifier with 3 classes
     # Compute accuracy using scikit-learn
     from sklearn.metrics import accuracy_score
     accuracy = accuracy_score(y_test, y_test_predictions)
     logger.info(f'Accuracy of the model: {accuracy}')
 
     # Compute the confusion matrix
     from sklearn.metrics import confusion_matrix
     confusion_matrix = confusion_matrix(y_test, y_test_predictions)
     logger.info(f'Confusion matrix of the model:')
     logger.info(confusion_matrix)
 
     # Compute the classification report
     from sklearn.metrics import classification_report   
     classification_report = classification_report(y_test, y_test_predictions)
     logger.info(f'Classification report of the model:')
     logger.info(classification_report)
 
 
 
 
def split_train_test(
     ohlc_data: pd.DataFrame,
     last_n_days_to_test_model: int
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
     cutoff_date = ohlc_data['datetime'].max() - pd.Timedelta(days=last_n_days_to_test_model)
 
     # split the data into training and testing
     ohlc_train = ohlc_data[ohlc_data['datetime'] < cutoff_date]
     ohlc_test = ohlc_data[ohlc_data['datetime'] >= cutoff_date]
     return ohlc_train, ohlc_test
 
 
def create_target_metric(
     ohlc_data: pd.DataFrame,
     ohlc_window_sec: int,
     discretization_thresholds: list,
     prediction_window_sec: int,
 ) -> pd.DataFrame:
     """
     Creates the target metric by 
     - discretizing the close price in the next prediction_window_sec
     - using the discretization_thresholds
     - and adds the final column in the output dataframe
 
     Args:
         ohlc_data (pd.DataFrame): The OHLC data.
         ohlc_window_sec (int): The size of the window in seconds.
         discretization_thresholds (list): The thresholds to discretize the close price.
         prediction_window_sec (int): The size of the prediction window in seconds.
 
     Returns:
         pd.DataFrame: The OHLC data with the target metric.
     """
     # check that prediction_window_sec is a multiple of ohlc_window_sec
     assert prediction_window_sec % ohlc_window_sec == 0, \
         'prediction_window_sec must be a multiple of ohlc_window_sec'
 
     n_candles_into_future = prediction_window_sec // ohlc_window_sec
 
     # create a new column with the percentage change in the close price n_candles_into_future
     ohlc_data['close_pct_change'] = ohlc_data['close'].pct_change(n_candles_into_future)
 
     # TODO
     # discretize the close_pct_change column using the discretization_thresholds
     # Not sure how the cut function works, so I will stick to what I know for now
     # Challenge: Check the documentation to see how the cut function works and use it
     # https://pandas.pydata.org/docs/reference/api/pandas.cut.html
     # ohlc_data['target'] = pd.cut(
     #     ohlc_data['close_pct_change'],
     #     bins=discretization_thresholds,
     #     labels=range(len(discretization_thresholds) - 1),
     # )
     def discretize(x: float) -> int:
         """
         Maps the given percentage change `x` to a discrete value based on the thresholds.
         """
         if x < discretization_thresholds[0]:
             # DOWN
             return 0
         elif x < discretization_thresholds[1]:
             # SAME
             return 1
         elif x >= discretization_thresholds[1]:
             # UP
             return 2
         else:
             # This will happen if x is NaN
             None
 
     ohlc_data['target'] = ohlc_data['close_pct_change'].apply(discretize)
 
     # shift the target column by n_candles_into_future to have the target for the current candle
     ohlc_data['target'] = ohlc_data['target'].shift(-n_candles_into_future)
 
     # drop the close_pct_change column
     ohlc_data.drop(columns=['close_pct_change'], inplace=True)
 
     # Anton Javelosa asked:
     # "Won't n rows at the end have blank targets? After the shift up?"
     # Yes, you are right. Let's drop them before returning the dataframe
     # Thanks Anton!
     ohlc_data.dropna(subset=['target'], inplace=True)
 
     return ohlc_data
 
 
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
     # otherwise you can do a copy. This is less efficient.
     # ohlc_data = ohlc_data.set_index('timestamp')
 
     # complete list of timestamps for which we need to have rows in our dataframe
     from_ms = ohlc_data.index.min()
     to_ms = ohlc_data.index.max()
     labels = range(from_ms, to_ms, ohlc_window_sec*1000)
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
 
if __name__ == '__main__':
 
     train(
         feature_view_name='ohlc_feature_view',
         feature_view_version=1,
         ohlc_window_sec=60,
         product_id='BTC/USD',
         last_n_days_to_fetch_from_store=90,
         last_n_days_to_test_model=7,
         discretization_thresholds=[-0.0001, 0.0001],
         prediction_window_sec=60*5,
    )