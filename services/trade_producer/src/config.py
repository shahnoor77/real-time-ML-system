import os

from dotenv import load_dotenv, find_dotenv
#kafka_broker_address = os.environ['KAFKA_BROKER_ADDRESS']
#kafka_topic_name = 'trade'
#product_id = 'ETH/USD'


from pydantic_settings import BaseSettings

load_dotenv(find_dotenv())

class Config(BaseSettings):
    product_id: str = 'ETH/USD'
    kafka_broker_address: str = os.environ['KAFKA_BROKER_ADDRESS']
    kafka_topic_name: str = 'trade'
    ohlc_windows_seconds: int = os.environ['OHLC_WINDOWS_SECONDS']


config =  Config()