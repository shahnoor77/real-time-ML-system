from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
from pydantic_settings import BaseSettings

load_dotenv(find_dotenv())

class Config(BaseSettings):
    kafka_broker_address: str = 'loaclhost:19092'
    feature_group_version: int
    hopsworks_api_key: str
    hopsworks_project_name: str 
    kafka_topic: str
    feature_group_name: str 
    buffer_size: int = 1
    live_or_historical :str = 'live' #by default we want this service to run in liv mode

    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields

config = Config()




