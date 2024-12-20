import os 
from dotenv import load_dotenv, find_dotenv
 #load my .env file variables as environment variables so i can access them
 #with os.environ[] statements

load_dotenv(find_dotenv())


from pydantic_settings import BaseSettings 

class config(BaseSettings):
    kafka_broker_address: str = os.environ['KAFKA_BROKER_ADDRESS']
    kafka_input_topic: str ="trade"
    kafka_output_topic:  str = "ohlc"
    ohlc_window_seconds: int = os.environ['OHLC_WINDOWS_SECONDS']
    

config = config()