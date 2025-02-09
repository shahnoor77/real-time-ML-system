run-dev:
	poetry run python src/main.py
	KAFKA_BROKER_ADDRESS='localhost:19092' \
	source live.env && poetry run python src/main.py
run-dev-historical:
	KAFKA_BROKER_ADDRESS='localhost:19092' \
	source historical.env && poetry run python src/main.py

build:
	docker build -t trade-to-ohlc .

run: build
	docker run \
		--network=redpanda_network \
		--env KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
		--env OHLC_WINDOW_SECONDS=60 \
		trade-to-ohlc

lint:
	poetry run ruff check --fix

format:
	poetry run ruff format .