run-dev:
	KAFKA_BROKER_ADDRESS='localhost:19092' \
	source setup_live_config.sh && poetry run python src/main.py

run-dev-historical:
	KAFKA_BROKER_ADDRESS='localhost:19092' \
	source setup_historical_config.sh && poetry run python src/main.py

	build:
	docker build -t trade-producer .

run: build
	docker run \
		--network=redpanda_network \
		-e KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
		-e KAFKA_TOPIC=trade \
		-e PRODUCT_IDS='["ETH/USD","BTC/USD","BTC/EUR","USDT/USD","USDT/USD"]' \
		-e LIVE_OR_HISTORICAL=live \
		trade-producer
run-historical: build
	docker run \
		--network=redpanda_network \
		-e KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
		-e KAFKA_TOPIC=trade_historical \
		-e PRODUCT_IDS='["ETH/USD","BTC/USD","BTC/EUR","USDT/USD","USDT/USD"]' \
		-e LIVE_OR_HISTORICAL=historical \
		-e LAST_N_DAYS=90 \
		trade-producer


lint:
	poetry run ruff check --fix

format:
	poetry run ruff format .