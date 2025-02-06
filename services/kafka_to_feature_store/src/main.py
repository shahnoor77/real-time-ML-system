from quixstreams import Application
from loguru import logger
from datetime import datetime, timezone
from typing import Optional
import json
from src.config import config
from src.hopsworks_api import push_data_to_feature_store


def get_current_utc_sec()->int:
    """
    Returns the current UTC time in seconds since the epoch.
    Args:
        None
    Returns:
        int: the current UTC time in seconds since the epoch.
            
    """
    return int(datetime.now(timezone.utc).timestamp())


def kafka_to_feature_store(
        kafka_topic           : str,           # get data from
        kafka_broker_address  : str,
        feature_group_name    : str,           # store data to 
        feature_group_version : int, 
        buffer_size           :Optional[int] = 1,    # buffer size for the feature store
        live_or_historical    : Optional[str] = 'live'
        
)->None:
    """
    Read 'ohlc' data from the specified Kafka topic and store it into the feature store.
    More specifically, it write the data into the feature group specified by
    "feature_group_name"  and "feature_group_version".
    
    Args:
        kafka_topic (str): The Kafka topic to read data from.
        kafka_broker_address (str): The address of the Kafka broker.
        feature_group_name (str): The name of the feature group to store data in.
        feature_group_version (int): The version of the feature group.
        buffer_size (int): The number of records to buffer before writing to the feature store.
        live_or_historical(str): whether we are saving live or historical data.
            live data goes to the online feature store,
            While historical data goes to the offline feature store.

    Returns:
          None
    """

       
    app = Application(

    broker_address= kafka_broker_address,
    consumer_group= "kafka_to_feature_store",
    #auto_offset_reset= "earliest", # start reading from the beginning of the topic
    
)
    # get UTC time in seconds
    last_saved_to_feature_store_ts = get_current_utc_sec()
    
    #TODO : handle the case when the buffer is not full but no more data is coming
    # with the current implementation we can have upto (buffer_size - 1) records in the buffer
    # that are not written to the feature store
    buffer = []
    with app.get_consumer() as consumer:
        consumer.subscribe(topics=[kafka_topic])

        while True:
            msg = consumer.poll(1)

            if msg is None:
                # there are no new messages in the kafka topic
                # instead of just skipping, we will check what was the last
                # time when we pushed feature to the feature store.
                # if more than N minutes are passed, we will push the data to the feature store.
                n_sec = 10
                logger.debug(f'No new messsage in the input topic {kafka_topic}')
                if(get_current_utc_sec() - last_saved_to_feature_store_ts) > n_sec:
                    logger.debug('Exeeded timer limit: we push the data to the feature store.')
                    push_data_to_feature_store(
                        feature_group_name = feature_group_name,
                        feature_group_version = feature_group_version,
                        data = buffer,
                        online_or_offline = 'online' if live_or_historical == 'live' else 'offline',
                    )
                    buffer = []
                else:
                    # we haven't hit the timer limit, so we skip and continue polling message
                    logger.debug('we have not hit the timer limit, skip and continue...')
                    #from the kafka topic
                    continue


            elif msg.error():
                logger.error("kafka error:", {msg.error()})
                continue

            else:
               # There is data we need now to send it to the feature store

               # 1. Parse the data from kafka into dictionary
                ohlc = json.loads(msg.value().decode('utf-8'))
                # add the data to the buffer
                
                buffer.append(ohlc)
                # breakpoint()
                # check if the buffer is full
                if len(buffer) >= buffer_size:
                    # push the data to the feature store
                    push_data_to_feature_store(
                        feature_group_name = feature_group_name,
                        feature_group_version = feature_group_version,
                        data = buffer,
                        online_or_offline = 'online' if live_or_historical == 'live' else 'offline',
                    )
                    # clear/reset the buffer
                    buffer = []
                    last_saved_to_feature_store_ts = get_current_utc_sec()

                # 2. Push the data to the feature store
                #push_data_to_feature_store(
                #   feature_group_name = feature_group_name,
                
                #    feature_group_version = feature_group_version,
                #    data = ohlc,
                #)

                # 3. Store the offset of the message    
                # for the auto-commit mechanism
                # It will send it to the kafka in the background
                # starting the messaga only after the message is processed enbale atleast one-delivery-at-a-time
                # guarantees.
                consumer.store_offsets(message=msg)

if __name__ == "__main__":

    logger.debug(config.model_dump())
    try:
        kafka_to_feature_store(
            kafka_topic = config.kafka_topic,
            kafka_broker_address = config.kafka_broker_address,
            feature_group_name = config.feature_group_name,
            feature_group_version = config.feature_group_version,
            buffer_size = config.buffer_size,
            live_or_historical= config.live_or_historical,
        )
    except KeyboardInterrupt:
        logger.info("Exiting.....")
   

                  
                    
    