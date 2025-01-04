from typing import Dict, List

from loguru import logger
from quixstreams import Application
from src.kraken_api.rest import KrakenRestApi
from src.kraken_api.websocket import KrakenWebsocketTradeAPI
from src.config import config
def produce_trades(
    kafka_broker_address: str,  # from where to get the trades
    kafka_topic_name: str,  # where to save the trades
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
    assert live_or_historical in {'live', 'historical'}, f'Invalid value for live_or_historical: {live_or_historical}'
    app = Application(broker_address=kafka_broker_address)

    topic = app.topic(name=kafka_topic_name, value_serializer='json')
    logger.info(f'creating the Kraken API instance...for {product_ids}')

    # create an instance of the KrakenWebsocketTradeAPI
    # for historical data, we use the KrakenRestApi
    
    if live_or_historical == 'live':
        kraken_api = KrakenWebsocketTradeAPI(product_ids=product_ids)
    else:
        import time
        # get current date at midnight usiing UTC
        from datetime import datetime 
        from datetime import timezone
        today_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        # today_date to mili seconds
        to_ms = int(today_date.timestamp() * 1000)
        from_ms = to_ms - last_n_days * 24 * 60 * 60 * 1000

        kraken_api = KrakenRestApi(
            product_ids=product_ids,
           #from_ms=from_ms,
           #to_ms=to_ms,
           last_n_days=last_n_days,
        )    

        logger.info('creating the producer...')
    # create a producer instance
    with app.get_producer() as producer:
        while True:
            #check whether we are done fetching the trades 
            if kraken_api.is_done():
                logger.info('done fetching the historical trades!')
                break
            # get the trades from the API

            trades: List[Dict] = kraken_api.get_trades()
            # iterate over the trades
            for trade in trades :
                # serialize the trade using the defined topic
                message = topic.serialize(key=trade['product_id'], value=trade)
                # produce a message to the kafka topic
                producer.produce(topic=topic.name, value=message.value, key=message.key)
                logger.info(trade)
               

            


if __name__ == '__main__':
    try:
        produce_trades(
            kafka_broker_address=config.kafka_broker_address,
            kafka_topic_name=config.kafka_topic_name,
            product_ids=config.product_ids,
            # extra parameters that i need when running the trade producer
            # against historical data from the kraken rest api
            live_or_historical=config.live_or_historical,
            last_n_days=config.last_n_days,
        )
    except KeyboardInterrupt:
        logger.info('exiting the producer...')
        
