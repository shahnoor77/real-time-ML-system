# standard library packages
from datetime import timedelta
from typing import Any, List, Optional, Tuple

# third-party packages
from loguru import logger
from quixstreams import Application

# your own local packages
from src.config import config

def init_ohlc_candle(value: dict) -> dict:
    """
    Initialize the OHLC candle with the first trade
    """
    return {
        'open': value['price'],
        'high': value['price'],
        'low': value['price'],
        'close': value['price'],
        'product_id': value['product_id'],

        # Uncomment this line if you plan to use `volume` in your feature engineering
        # For you Olanrewaju!
        # 'volume': value['volume']
    }

def update_ohlc_candle(ohlc_candle: dict, trade: dict) -> dict:
    """
    Update the OHLC candle with the new trade and return the updated candle

    Args:
        ohlc_candle : dict : The current OHLC candle
        trade : dict : The incoming trade

    Returns:
        dict : The updated OHLC candle
    """
    return {
        'open': ohlc_candle['open'],
        'high': max(ohlc_candle['high'], trade['price']),
        'low': min(ohlc_candle['low'], trade['price']),
        'close': trade['price'],
        'product_id': trade['product_id'],

        # Uncomment this line if you plan to use `volume` in your feature engineering
        # For you Olanrewaju!
        # 'volume': ohlc_candle['volume'] + trade['volume']
    }

def custom_ts_extractor(
    value: Any,
    headers: Optional[List[Tuple[str, bytes]]],
    timestamp: float,
    timestamp_type,  #: TimestampType,
) -> int:
    """
    Specifying a custom timestamp extractor to use the timestamp from the message payload
    instead of Kafka timestamp.

    We want to use the `timestamp_ms` field from the message value, and not the timestamp
    of the message that Kafka generates when the message is saved into the Kafka topic.
    
    See the Quix Streams documentation here
    https://quix.io/docs/quix-streams/windowing.html#extracting-timestamps-from-messages
    """
    return value['timestamp_ms']


def trade_to_ohlc(
    kafka_input_topic: str,
    kafka_output_topic: str,
    kafka_broker_address: str,
    kafka_consumer_group: str,
    ohlc_window_seconds: int,
) -> None:
    """
    Reads trades from the kafka input topic
    Aggregates them into OHLC candles using the specified window in `ohlc_window_seconds`
    Saves the ohlc data into another kafka topic

    Args:
        kafka_input_topic : str : Kafka topic to read trade data from
        kafka_output_topic : str : Kafka topic to write ohlc data to
        kafka_broker_address : str : Kafka broker address
        kafka_consumer_group : str : Kafka consumer group
        ohlc_window_seconds : int : Window size in seconds for OHLC aggregation

    Returns:
        None
    """
    # this handles all low level communication with kafka
    app = Application(
        broker_address=kafka_broker_address,
        consumer_group=kafka_consumer_group,
        auto_offset_reset='latest',
    )

    # specify input and output topics for this application
    input_topic = app.topic(
        name=kafka_input_topic,
        value_serializer='json',
        timestamp_extractor=custom_ts_extractor,
    )
    output_topic = app.topic(name=kafka_output_topic, value_serializer='json')

    # creating a streaming dataframe
    # to apply transformations on the incoming data
    sdf = app.dataframe(input_topic)

    # apply tranformations to the incoming data - start
    # Here we need to define how we transform the incoming trades into OHLC candles
    sdf = sdf.tumbling_window(duration_ms=timedelta(seconds=ohlc_window_seconds))
    sdf = sdf.reduce(reducer=update_ohlc_candle, initializer=init_ohlc_candle).final()

    # extract the open, high, low, close prices from the value key
    # The current format is the following:
    # {
    #     'start': 1717667940000,
    #     'end': 1717668000000,
    #     'value':
    #         {'open': 3535.98, 'high': 3537.11, 'low': 3535.98, 'close': 3537.11, 'product_id': 'ETH/USD'}
    # }
    # But the message format we want is the following:
    # {
    #     'timestamp': 1717667940000, # end of the window
    #     'open': 3535.98,
    #     'high': 3537.11,
    #     'low': 3535.98,
    #     'close': 3537.11,
    #     'product_id': 'ETH/USD',
    # }

    # unpacking the values we want
    sdf['open'] = sdf['value']['open']
    sdf['high'] = sdf['value']['high']
    sdf['low'] = sdf['value']['low']
    sdf['close'] = sdf['value']['close']
    sdf['product_id'] = sdf['value']['product_id']

    # adding the volume key if you plan to use it generate features that depend on it
    # For you Olanrewaju!
    # sdf['volume'] = sdf['value']['volume']

    # adding a timestamp key
    sdf['timestamp'] = sdf['end']

    # let's keep only the keys we want in our final message
    # don't forget to add the volume key if you plan to use it
    sdf = sdf[['timestamp', 'open', 'high', 'low', 'close', 'product_id']]

    # apply tranformations to the incoming data - end

    # let's print the data to the logs
    sdf = sdf.update(logger.info)

    # write the data to the output topic
    sdf = sdf.to_topic(output_topic)

    # We are done defining the streaming application. Now we need to run it.
    # Let's kick-off the streaming application
    app.run(sdf)


if __name__ == '__main__':
    from src.config import config

    trade_to_ohlc(
        kafka_input_topic=config.kafka_input_topic,
        kafka_output_topic=config.kafka_output_topic,
        kafka_broker_address=config.kafka_broker_address,
        kafka_consumer_group=config.kafka_consumer_group,
        ohlc_window_seconds=config.ohlc_window_seconds,
    )