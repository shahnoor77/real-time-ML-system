import os

from dotenv import load_dotenv, find_dotenv

from pydantic_settings import BaseSettings

load_dotenv(find_dotenv())

class  Config(BaseSettings):

    kafka_broker_address: str = os.environ['KAFKA_BROKER_ADDRESS']
    kafka_input_topic:str  = 'trade'        #= os.environ['KAFKA_INPUT_TOPIC']
    kafka_output_topic:str = 'ohlc'       #= os.environ['KAFKA_OUTPUT_TOPIC']
    ohlc_windows_seconds: int = os.environ['OHLC_WINDOWS_SECONDS']

config = Config()