from typing import Optional

import pandas as pd
from sklearn.linear_model import Lasso
from xgboost import XGBRegressor


def fit_xgboost_regressor(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    tune_hyper_params: Optional[bool] = False,
) -> XGBRegressor:
    """
    """
    model = XGBRegressor()
    model.fit(X_train, y_train)
    return model
 
def fit_lasso_regressor(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    tune_hyper_params: Optional[bool] = False,
) -> Lasso:
    """
    """
    model = Lasso(alpha=0.1)
    model.fit(X_train, y_train)
    return model