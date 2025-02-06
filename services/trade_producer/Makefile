# Makefile

.PHONY: run-dev-historical run-dev-live build run run-historical lint format lint-and-format

# Rule for running in historical mode
run-dev-historical:
	@echo "Running trade_producer in historical mode with LAST_N_DAYS=7..."
	
	set LAST_N_DAYS=7 && set LIVE_OR_HISTORICAL=historical && poetry run python src/main.py

# Rule for running in live mode
run-dev-live:
	@echo "Running trade_producer in live mode..."
	# Set the mode to live or any other necessary configurations
	set LIVE_OR_HISTORICAL=live && poetry run python src/main.py

# Docker build rule
build:
	docker build -t trade-producer .

# Docker run rule for live mode
run: build
	docker run \
		--network=redpanda_network \
		-e KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
		-e KAFKA_TOPIC=trade \
		-e PRODUCT_IDS='["BTC/USD"]' \
		-e LIVE_OR_HISTORICAL=live \
		trade-producer

# Docker run rule for historical mode
run-historical: build
	docker volume create trade-producer-volume
	docker run \
		--network=redpanda_network \
		-e KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
		-e KAFKA_TOPIC=trade_historical \
		-e PRODUCT_IDS='["BTC/USD"]' \
		-e LIVE_OR_HISTORICAL=historical \
		-e LAST_N_DAYS=90 \
		-e CACHE_DIR_HISTORICAL_DATA=/tmp/historical_trade_data \
		-v trade-producer-volume:/tmp/historical_trade_data \
		trade-producer

# Linting rule
lint:
	poetry run ruff check --fix

# Formatting rule
format:
	poetry run ruff format .

# Lint and format in a single command
lint-and-format: lint format
