# Load environment variables from .env file
ifneq ($(wildcard .env),)
  include .env
  export
endif

# Default target
all: run

# Build the Docker image
build:
	docker build -t feature_dashboard .

# Run the Docker container
run: build
	docker run \
		--env-file .env \
		-e HOPSWORKS_API_KEY=$(HOPSWORKS_API_KEY) \
		-e HOPSWORKS_PROJECT_NAME=$(HOPSWORKS_PROJECT_NAME) \
		-e PRODUCT_ID=$(PRODUCT_ID) \
		-e FEATURE_GROUP_NAME=$(FEATURE_GROUP_NAME) \
		-e FEATURE_GROUP_VERSION=$(FEATURE_GROUP_VERSION) \
		-e FEATURE_VIEW_NAME=$(FEATURE_VIEW_NAME) \
		-e FEATURE_VIEW_VERSION=$(FEATURE_VIEW_VERSION) \
		feature_dashboard:latest

