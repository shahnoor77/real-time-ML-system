from quixstreams import Application
from loguru import logger
import json
from src.config import config
from src.hopsworks_api import push_data_to_feature_store



def kafka_to_feature_store(
        kafka_topic           : str,           # get data from
        kafka_broker_address  : str,
        feature_group_name    : str,           # store data to 
        feature_group_version : int, 
        buffer_size           : int = 1,    # buffer size for the feature store
        
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

    Returns:
          None
    """
       
    app = Application(

    broker_address= kafka_broker_address,
    consumer_group= "kafka_to_feature_store",
    auto_offset_reset= "earliest", # start reading from the beginning of the topic
    
)
    #TODO : handle the case when the buffer is not full but no more data is coming
    # with the current implementation we can have upto (buffer_size - 1) records in the buffer
    # that are not written to the feature store
    buffer = []
    with app.get_consumer() as consumer:
        consumer.subscribe(topics=[kafka_topic])

        while True:
            msg = consumer.poll(1)
            if msg is None:
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
                    )
                    # clear/reset the buffer
                    buffer = []

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
        )
    except KeyboardInterrupt:
        logger.info("Exiting.....")
   

                  
                    
    