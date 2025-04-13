import json
from typing import Optional

from loguru import logger
from quixstreams import Application

from src.hopsworks_api import push_data_to_feature_store


def get_current_utc_sec() -> int:
    """
    Returns the current UTC time expressed in seconds since the epoch.

    Args:
        None

    Returns:
        int: The current UTC time expressed in seconds since the epoch.
    """
    from datetime import datetime, timezone

    return int(datetime.now(timezone.utc).timestamp())


def kafka_to_feature_store(
    kafka_topic: str,
    kafka_broker_address: str,
    kafka_consumer_group: str,
    feature_group_name: str,
    feature_group_version: int,
    buffer_size: Optional[int] = 1,
    live_or_historical: Optional[str] = 'live',
    save_every_n_sec: Optional[int] = 600,
    create_new_consumer_group: Optional[bool] = False,
) -> None:
    """
    Reads `ohlc` data from the Kafka topic and writes it to the feature store.
    More specifically, it writes the data to the feature group specified by
    - `feature_group_name` and `feature_group_version`.

    Args:
        kafka_topic (str): The Kafka topic to read from.
        kafka_broker_address (str): The address of the Kafka broker.
        kafka_consumer_group (str): The Kafka consumer group we use for reading messages.
        feature_group_name (str): The name of the feature group to write to.
        feature_group_version (int): The version of the feature group to write to.
        buffer_size (int): The number of messages to read from Kafka before writing to the feature store.
        live_or_historical (str): Whether we are saving live data to the Feature or historical data.
            Live data goes to the online feature store
            While historical data goes to the offline feature store.
        save_every_n_sec (int): The max seconds to wait before writing the data to the
            feature store.
        create_new_consumer_group (bool): Whether to create a new consumer group or not.

    Returns:
        None
    """
    # to force your application to read from the beginning of the topic
    # you need 2 things:
    # 1. Create a unique consumer group name
    # 2. Set the auto_offset_reset to 'earliest' -> offset for this new consuemr group is 0.
    # Which means that when you spin up the `kafka_to_feature_store` service again, it 
    # will re-process all the messages in the topic `kafka_topic`
    if create_new_consumer_group:
        # generate a unique consumer group name using uuid
        import uuid
        kafka_consumer_group = 'ohlc_historical_consumer_group_' + str(uuid.uuid4())
        logger.debug(f'New consumer group name: {kafka_consumer_group}')

    # breakpoint()

    app = Application(
        broker_address=kafka_broker_address,
        consumer_group=kafka_consumer_group,
        auto_offset_reset="earliest" if live_or_historical == 'historical' else "latest",
        # auto_offset_reset='latest',
    )

    # let's connect the app to the input topic
    topic = app.topic(name=kafka_topic, value_serializer='json')

    # get current UTC time in seconds
    last_saved_to_feature_store_ts = get_current_utc_sec()

    # contains the list of trades to be written to the feature store at once
    # TODO: handle the case where there the last batch is not full but no more data is
    # coming. With the current implementation we can have up to (buffer_size - 1) messages
    # in the buffer that will never be written to the feature store.
    buffer = []

    # Create a consumer and start a polling loop
    with app.get_consumer() as consumer:
        consumer.subscribe(topics=[topic.name])

        while True:
            msg = consumer.poll(1)

            # number of seconds since the last time we saved data to the feature store
            sec_since_last_saved = (
                get_current_utc_sec() - last_saved_to_feature_store_ts
            )

            if (msg is not None) and msg.error():
                # We have a message but it is an error.
                # We just log the error and continue
                logger.error('Kafka error:', msg.error())
                continue

            elif (msg is None) and (sec_since_last_saved < save_every_n_sec):
                # There are no new messages in the input topic and we haven't hit the timer
                # limit yet. We skip and continue polling messages from Kafka.
                logger.debug('No new messages in the input topic')
                logger.debug(
                    f'Last saved to feature store {sec_since_last_saved} seconds ago (limit={save_every_n_sec})'
                )
                # logger.debug(f'We have not hit the {save_every_n_sec} second limit.')
                continue

            else:
                # either we have a message or we have hit the timer limit
                # if we have a message we need to add it to the buffer
                if msg is not None:
                    # append the data to the buffer
                    ohlc = json.loads(msg.value().decode('utf-8'))
                    buffer.append(ohlc)
                    logger.debug(
                        f'Message {ohlc} was pushed to buffer. Buffer size={len(buffer)}'
                    )

                    # # Store the offset of the processed message on the Consumer
                    # # for the auto-commit mechanism.
                    # # It will send it to Kafka in the background.
                    # # Storing offset only after the message is processed enables at-least-once delivery
                    # # guarantees.
                    # consumer.store_offsets(message=msg)

                # if the buffer is full or we have hit the timer limit,
                # we write the data to the feature store
                if (len(buffer) >= buffer_size) or (
                    sec_since_last_saved >= save_every_n_sec
                ):
                    # if the buffer is not empty we write the data to the feature store
                    if len(buffer) > 0:
                        try:
                            push_data_to_feature_store(
                                feature_group_name=feature_group_name,
                                feature_group_version=feature_group_version,
                                data=buffer,
                                online_or_offline='online'
                                if live_or_historical == 'live'
                                else 'offline',
                            )
                            logger.debug('Data pushed to the feature store')

                        except Exception as e:
                            logger.error(
                                f'Failed to push data to the feature store: {e}'
                            )
                            continue

                        # reset the buffer
                        # Thanks Rosina!
                        buffer = []

                        last_saved_to_feature_store_ts = get_current_utc_sec()


if __name__ == '__main__':
    from src.config import config

    logger.debug(config.model_dump())

    try:
        kafka_to_feature_store(
            kafka_topic=config.kafka_topic,
            kafka_broker_address=config.kafka_broker_address,
            kafka_consumer_group=config.kafka_consumer_group,
            feature_group_name=config.feature_group_name,
            feature_group_version=config.feature_group_version,
            buffer_size=config.buffer_size,
            live_or_historical=config.live_or_historical,
            save_every_n_sec=config.save_every_n_sec,
            create_new_consumer_group=config.create_new_consumer_group,
        )
    except KeyboardInterrupt:
        logger.info('Exiting neatly!')