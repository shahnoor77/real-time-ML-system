from quixstreams import Application

def trade_to_ohlc(
    kafka_input_topic: str,
    kafka_output_topic: str,
    kafka_broker_address: str,
    ohlc_window_seconds: int,
) -> None:
    """
    Reads trades from the Kafka input topic,
    aggregates them into OHLC candles using the specified window in "ohlc_window_second,"
    and writes the OHLC data to the Kafka output topic.

    Args:
        kafka_input_topic (str): Kafka topic to read trade data from.
        kafka_output_topic (str): Kafka topic to write OHLC data to.
        kafka_broker_address (str): Kafka broker address.
        ohlc_window_second (int): Window size in seconds for OHLC aggregation.

    Returns:
        None
    """
    app = Application(
        broker_address=kafka_broker_address,
        consumer_group="trade_to_ohlc"
    )
    # Specify input and output topics for this application
    input_topic = app.topic(name=kafka_input_topic, value_serializer='json')
    output_topic = app.topic(name=kafka_output_topic, value_serializer='json')

    # Create a streaming DataFrame
    sdf = app.dataframe(input_topic)

    # TODO: Apply transformations to the incoming data
    # Example: sdf = sdf.groupby("timestamp").aggregate(["open", "high", "low", "close"])

    # Publish transformed data to the output topic
    sdf = sdf.to_topic(output_topic)

    # Start the streaming application
    app.run(sdf)

if __name__ == '__main__':
    from src.config import config

    trade_to_ohlc(
        kafka_input_topic=config.kafka_input_topic,
        kafka_output_topic=config.kafka_output_topic,
        kafka_broker_address=config.kafka_broker_address,
        ohlc_window_seconds=config.ohlc_window_seconds,
    )
