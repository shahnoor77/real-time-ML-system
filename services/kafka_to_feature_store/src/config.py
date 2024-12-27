import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    kafka_broker_address: str
    feature_group_version: int
    hopsworks_api_key: str
    hopsworks_project_name: str 
    kafka_topic: str
    feature_group_name: str 

    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields

config = Config()




