import pandas as pd
 
 
class BaselineModel:
 
     def __init__(
         self,
         n_candles_into_future: int,
         discretization_thresholds: list,
     ):
         self.n_candles_into_future = n_candles_into_future
         self.discretization_thresholds = discretization_thresholds
 
     def predict(self, X: pd.DataFrame) -> pd.Series:
         """
         To predict the target metric for a given row of X, we compute the last observed
         target metric (aka the last observer price change) and we use that as our
         prediction
         """
         X_= X.copy()
 
         X_['close_pct_change'] = X_['close'].pct_change(self.n_candles_into_future)
         X_['target'] = X_['close_pct_change'].apply(self._discretize)
 
         # the first `n_candles_into_future` rows will have NaN as target
         # because we don't have historical data to compute the pct_change
         # in this case we will predict the 1 class, which means the price will stay the same
         X_['target'].fillna(1, inplace=True)
         
         return X_['target']
 
         # Python trick -> you can do the same with this 3-liner
         # It's equivalent but looks nicer.
         # return X['close'] \
         #         .pct_change(self.n_candles_into_future) \
         #         .apply(self._discretize)
     
 
     def _discretize(self, x: float) -> int:
         """
         Maps the given percentage change `x` to a discrete value based on the thresholds.
         """
         if x < self.discretization_thresholds[0]:
             # DOWN
             return 0
         elif x < self.discretization_thresholds[1]:
             # SAME
             return 1
         elif x >= self.discretization_thresholds[1]:
             # UP
             return 2
         else:
             # This will happen if x is NaN
             None
