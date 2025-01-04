import hopsworks
from src.config import config
import pandas as pd
from typing import List, Dict
def push_data_to_feature_store(
        feature_group_name    : str,      
        feature_group_version : int,
        data                  : List[dict],
)->None:
    """
     Pushes the given data to the feature store, writing it to the feature group with name
    "feature_group_name"  and "feature_group_version".
    
    Args:
        feature_group_name (str): The name of the feature group to store data in.
        feature_group_version (int): The version of the feature group.
        data (list[dict]): The data to store in the feature group.
        
    Returns:
          None
    """
    # Authenticate with Hopsworks API
    project= hopsworks.login(
        project= config.hopsworks_project_name,
        api_key_value= config.hopsworks_api_key,
    )
    # Get the feature store 

    feature_store = project.get_feature_store()
    # Get or create the feature group that will store the data
    # To get or create a feature group, we need to specify the name of the feature group and the version of the feature group.
    # If the feature group does not exist, it will be created.

    ohlc_feature_group = feature_store.get_or_create_feature_group(
        name = feature_group_name,
        version = feature_group_version,
        description = 'Feature group for storing OHLC data',
        primary_key = ["product_id", "timestamp"],
        event_time = "timestamp",
        online_enabled = True,
    )
    

    #transform the data into a pandas dataframe
    #breakpoint()
    df = pd.DataFrame(data)

    # Write the data to the feature group
    ohlc_feature_group.insert(data, write_options = {"start_offline_meterialization": False}) #this will not write data from online feature store to offline feature store
    # materializing means writing data from online feature store to offline feature store
    

  