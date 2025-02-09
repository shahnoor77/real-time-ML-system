import json
from typing import Dict, List
from loguru import logger
from quixstreams import Application
from src.config import config
from src.kraken_api.rest import KrakenRestApiMultipleProducts
from src.kraken_api.websocket import KrakenWebsocketTradeAPI
from src.kraken_api.trade import Trade

def produce_trades(
    kafka_broker_address: str,  # from where to get the trades
    kafka_topic: str,  # where to save the trades
    product_ids: List[str],  # which trades to get
    live_or_historical: str,  # live or historical trades
    last_n_days: int,  # how many days of historical trades to get
)-> None:
    """
    Args:
        kafka_broker_address (str): The address of the Kafka broker.
        kafka_topic_name (str): The name of the Kafka topic.
        product_ids (List[str]): The list of product ids.
        live_or_historical (str): The type of trades to get.
        last_n_days (int): The number of days of historical trades to get.
    Returns:
        None
    """
    #assert live_or_historical in {'live', 'historical'}, f'Invalid value for live_or_historical: {live_or_historical}'
    
    # Create an Application instance to interact with Kafka
    app = Application(broker_address=kafka_broker_address)

    # Create a Kafka topic with a JSON serializer for the values
    topic = app.topic(name=kafka_topic, value_serializer='json')
    logger.info(f'Creating the Kraken API to fetch data for {product_ids}')

    # Instantiate the appropriate Kraken API based on the trade type (live or historical)
    if live_or_historical == 'live':
        kraken_api = KrakenWebsocketTradeAPI(product_ids=product_ids)
    else:
        kraken_api = KrakenRestApiMultipleProducts(
            product_ids=product_ids,
            last_n_days=last_n_days,
        )    

    logger.info('Creating the Kafka producer...')
    
    # Start the producer within a context manager to ensure proper cleanup
    with app.get_producer() as producer:
        while True:
            # Check whether we've finished fetching all historical trades
            if kraken_api.is_done():
                logger.info('Done fetching the historical trades!')
                break
            
            # Get a list of trades from the Kraken API
            trades: List[Trade] = kraken_api.get_trades()
            
            # Iterate over the list of trades
            for trade in trades:
                message = topic.serialize(
                    key=trade.product_id,
                    value = trade.model_dump(),
                )
                # Serialize the trade and key, ensuring they're in the correct format for Kafka
                # Produce the trade message to Kafka
                producer.produce(topic=topic.name,
                                value= message.value,
                                key=message.key
                )
                
                # Log the trade for monitoring purposes
                logger.info(trade)


if __name__ == '__main__':

    logger.debug('Configuration:')
    logger.debug(config.model_dump())
    try:
        produce_trades(
            kafka_broker_address=config.kafka_broker_address,
            kafka_topic_name=config.kafka_topic,
            product_ids=config.product_ids,
            live_or_historical=config.live_or_historical,
            last_n_days=config.last_n_days,
        )
    except KeyboardInterrupt:
        logger.info('Exiting the producer...')
