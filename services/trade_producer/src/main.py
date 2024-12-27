from quixstreams import Application

from src.kraken_api import KrakenWebsocketTradeAPI
from typing import List, Dict
def produce_trades(
        kafka_broker_address: str,  # from where to get the trades
        kafka_topic_name: str,  # where to save the trades

)->None:
    """
    Args:
        kafka_broker_address (str): The address of the Kafka broker.
        kafka_topic_name (str): The name of the Kafka topic.
    Returns:
        None
    """

    app = Application(broker_address=kafka_broker_address)  

    topic = app.topic(name=kafka_topic_name, value_serializer='json')
    
    # create an instance of the KrakenWebsocketTradeAPI
    kraken_api = KrakenWebsocketTradeAPI(product_id='BTC-USD')

    # create a producer instance
    with app.get_producer() as producer:

        while True:
            # get the trades from the API

            
            trades : List[Dict] = kraken_api.get_trades()
            # iterate over the trades
            for trade in trades:
                # serialize the trade using the defined topic
                message = topic.serialize(key = trade["product_id"], value = trade)
                # produce a message to the kafka topic
                producer.produce(
                    topic = topic.name,
                    value =  message.value,
                    key = message.key
                )
                print(f"Produced message: {message.value}")
                from time import sleep
                sleep(1)

if __name__ == '__main__':

    produce_trades(kafka_broker_address='localhost:19092',
                    kafka_topic_name='trade'
    )