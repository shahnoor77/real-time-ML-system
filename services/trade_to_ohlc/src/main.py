from quixstreams import Application
from datetime import timedelta
from loguru import logger
def trade_to_ohlc(
    kafka_input_topic   : str,
    kafka_output_topic  : str,
    kafka_broker_address: str,
    ohlc_window_seconds : int,
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
        broker_address    =  kafka_broker_address,
        consumer_group    = "trade_to_ohlc",
        #auto_offset_reset = "earliest", # process all message from the input topic when this service starts
        #auto_create_reset = "latest",   #forget about the past messages, poduce only the once coming that moment 
    )
    # Specify input and output topics for this application
    input_topic  = app.topic(name=kafka_input_topic, value_serializer='json')
    output_topic = app.topic(name=kafka_output_topic, value_serializer='json')

    # Create a streaming DataFrame
    sdf = app.dataframe(input_topic)

    def init_ohlc_candle(value:dict)->dict:
        """
        Initialize the OHLC candle with the first trade

        """
        return{
            "open"  : value["price"],
            "high"  : value["price"],
            "low"   : value["price"],
            "close" : value["price"],
            "product_id":value["product_id"],
        }

    def update_ohlc_candle(ohlc_candle : dict, trade : dict)->dict:
        """
           update the ohlc candle with the new trade and returns the updated candle
        Args:
            ohlc_candle : dict, the current ohlc candle
            trade       : dict, the new trade
        return:
            dict : the updated candle

        """
        return{
            "open"       : ohlc_candle["open"],
            "high"       : max(ohlc_candle["high"], trade["price"]),
            "low"        : min(ohlc_candle["low"], trade["price"]),
            "close"      : trade["price"],
            "product_id" : trade["product_id"],
        }


    # TODO: Apply transformations to the incoming data-start
    # Here we need to describe how we trnsform the incoming trades into ohlc candles
    sdf = sdf.tumbling_window(duration_ms=timedelta(seconds=ohlc_window_seconds))
    sdf = sdf.reduce(reducer=update_ohlc_candle, initializer=init_ohlc_candle).current()

    # Example: sdf = sdf.groupby("timestamp").aggregate(["open", "high", "low", "close"])
    # Unpacking the value we want
    sdf['open']  = sdf['value']['open']
    sdf['high']  = sdf['value']['high']
    sdf['low']   = sdf['value']['low']
    sdf['close'] = sdf['value']['close']
    sdf['product_id'] = sdf['value']['product_id']

    # Adding a timestamp key
    sdf['timestamp']  = sdf['end']

    # let's keep only the keys we want in our final message!
    sdf = sdf[['timestamp', 'open', 'high', 'low', 'close', 'product_id']]
    # Apply transformations to the incoming data-end

    sdf = sdf.update(logger.info)
    # Publish transformed data to the output topic
    sdf = sdf.to_topic(output_topic)

    # Start the streaming application
    app.run(sdf)

if __name__ == '__main__':
    from src.config import config

    trade_to_ohlc(
        kafka_input_topic    =config.kafka_input_topic,
        kafka_output_topic   =config.kafka_output_topic,
        kafka_broker_address =config.kafka_broker_address,
        ohlc_window_seconds  =config.ohlc_window_seconds,
    )


