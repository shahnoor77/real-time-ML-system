import hopsworks
from src.config import config
import pandas as pd
def push_data_to_feature_store(
        feature_group_name    : str,      
        feature_group_version : int,
        data                  : dict,
)->None:
    """
     Pushes the given data to the feature store, writing it to the feature group with name
    "feature_group_name"  and "feature_group_version".
    
    Args:
        feature_group_name (str): The name of the feature group to store data in.
        feature_group_version (int): The version of the feature group.
        data (dict): The data to store in the feature group.
        
    Returns:
          None
    """
    # Authenticate with Hopsworks API
    project= hopsworks.login(
        project= config.hopsworks_project_name,
        api_key_value= config.hopsworks_api_key,
    )
    # Get the feature store 

    feature_store = project.get_featurestore()
    # Get or create the feature group that will store the data
    # To get or create a feature group, we need to specify the name of the feature group and the version of the feature group.
    # If the feature group does not exist, it will be created.

    ohlc_feature_group = feature_store.get_feature_group(
        name = feature_group_name,
        version = feature_group_version,
        description = "Feature group for storing OHLC data",
        primary_key = ["product_id", "timestamp"],
        event_time = "timestamp",
        enabled_online = True,
    )

    #transform the data into a pandas dataframe

    df = pd.DataFrame([data])

    # Write the data to the feature group
    ohlc_feature_group.insert(df)
    

  