from typing import Optional

from pydantic_settings import BaseSettings

# load my .env file variables as environment variables so pydantic_settings can access them
# to create the Config object
# load_dotenv(find_dotenv())


class Config(BaseSettings):
    """
    Configuration settings for the trade_to_ohlc service

    Attributes:
        kafka_broker_address (str): The address of the Kafka broker.
        kafka_input_topic (str): The name of the Kafka topic where the trade data is read from.
        kafka_output_topic (str): The name of the Kafka topic where the OHLC data is written to.
        ohlc_window_seconds (int): The window size in seconds for OHLC aggregation.

    Values are read from environment variables.
    If they are not found there, default values are used.
    """

    kafka_broker_address: Optional[str] = None
    kafka_input_topic: str
    kafka_output_topic: str
    kafka_consumer_group: str
    ohlc_window_seconds: int


config = Config()