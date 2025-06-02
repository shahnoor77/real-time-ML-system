.PHONY: train predict api request invalid-request

train:
	poetry run python src/training.py

predict:
	poetry run python src/predictor.py

api:
	poetry run python src/api.py

request:
	curl -X POST http://127.0.0.1:5000/predict -H "Content-Type: application/json" -d '{"product_id":"BTC/USD"}'

invalid-request:
	curl -X POST http://127.0.0.1:5005/predict -H "Content-Type: application/json" -d '{"product_id":"ETH/USD"}'

build:
	docker build -t price-predictor-api .
    