export KAFKA_TOPIC=ohlc
export KAFKA_CONSUMER_GROUP=ohlc_consumer_group_99
export FEATURE_GROUP_NAME=ohlc_feature_group
export FEATURE_GROUP_VERSION=1

# number of elements we save at once to the Hopsworks feature store
# For live data we want to save it to the online store as soon as possible,
# so we set this to 1
export BUFFER_SIZE=1

# this way we tell  our `kafka_to_feature_store` service to save features to the
# offline store, because we are basically generating historical data we will use for
# training our models
export LIVE_OR_HISTORICAL=live