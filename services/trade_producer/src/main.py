from typing import Dict, List

from loguru import logger
from quixstreams import Application

from src.kraken_api import KrakenWebsocketTradeAPI
from src.config import config
def produce_trades(
    kafka_broker_address: str,  # from where to get the trades
    kafka_topic_name: str,  # where to save the trades
    product_id : str,
) -> None:
    """
    Args:
        kafka_broker_address (str): The address of the Kafka broker.
        kafka_topic_name (str): The name of the Kafka topic.
        product_id (str): The product id of the trades to get.
    Returns:
        None
    """

    app = Application(broker_address=kafka_broker_address)

    topic = app.topic(name=kafka_topic_name, value_serializer='json')

    # create an instance of the KrakenWebsocketTradeAPI
    kraken_api = KrakenWebsocketTradeAPI(product_id=product_id)
    logger.info('creating the producer...')
    # create a producer instance
    with app.get_producer() as producer:
        while True:
            # get the trades from the API

            trades: List[Dict] = kraken_api.get_trades()
            # iterate over the trades
            for trade in trades:
                # serialize the trade using the defined topic
                message = topic.serialize(key=trade['product_id'], value=trade)
                # produce a message to the kafka topic
                producer.produce(topic=topic.name, value=message.value, key=message.key)
                logger.info('message sent!')
                from time import sleep

                sleep(1)


if __name__ == '__main__':
    produce_trades(kafka_broker_address=config.kafka_broker_address,
                   kafka_topic_name=config.kafka_topic_name,
                   product_id=config.product_id,
    )
