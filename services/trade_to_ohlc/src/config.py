import os

from dotenv import load_dotenv, find_dotenv

from pydantic_settings import BaseSettings

load_dotenv(find_dotenv())

class  Config(BaseSettings):

    kafka_broker_address: str 
    kafka_input_topic:str  = ('trade')       #= os.environ['KAFKA_INPUT_TOPIC']
    kafka_output_topic:str = ('ohlc')       #= os.environ['KAFKA_OUTPUT_TOPIC']
    ohlc_windows_seconds: int 

config = Config()