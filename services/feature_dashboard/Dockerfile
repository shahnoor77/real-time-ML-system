FROM python:3.10.3-slim-buster

# Install GCC and Python3-dev to compile Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Set environment variable to stream output to console
ENV PYTHONUNBUFFERED=1

# Install poetry inside the container
RUN pip install poetry==1.8.5

# Set the working directory inside the container
WORKDIR /app

# Add /app to PYTHONPATH (not just /app/src)
ENV PYTHONPATH=/app

# Copy pyproject.toml and poetry.lock into the container
COPY pyproject.toml poetry.lock /app/

# Install Python dependencies using Poetry
RUN poetry install 

# Copy the source code into the container
COPY src /app/src

# Run the application using Poetry
CMD ["poetry", "run", "python", "src/frontend.py"]
