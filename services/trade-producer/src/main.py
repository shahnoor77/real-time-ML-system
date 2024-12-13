from quixstreams import Application


def produce_trades(
    kaka_broker_address: str,
    kaka_topic_name: str,
) -> None:
    """
    Reads trades from the Kraken websocket API and saves them into a Kafka topic.

    Args:
        kaka_broker_address (str): The address of the Kafka broker.
        kaka_topic_name (str): The name of the Kafka topic.

    Returns:
        None
    """
    app = Application(broker_address=kaka_broker_address)

    # the topic where we will save the trades
    topic = app.topic(name=kaka_topic_name, value_serializer='json')

    event = {"id": "1", "text": "Lorem ipsum dolor sit amet"}

    # Create a Producer instance
    with app.get_producer() as producer:

        while True:
            # Serialize an event using the defined Topic 
            message = topic.serialize(key=event["id"], value=event)

            # Produce a message into the Kafka topic
            producer.produce(
                topic=topic.name,
                value=message.value,
                key=message.key
            )

            print('Message sent!')
            
            from time import sleep
            sleep(1)

if __name__ == '__main__':

    produce_trades(
        kaka_broker_address="localhost:19092",
        kaka_topic_name="trade"
    )