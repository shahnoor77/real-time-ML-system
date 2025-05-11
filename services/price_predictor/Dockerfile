# Use a Python 3.10 slim image as the base image
FROM python:3.10.3-slim-buster

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc wget build-essential \
    python3-dev libssl-dev libffi-dev \
    gfortran libopenblas-dev liblapack-dev \
    ca-certificates curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install TA-Lib from source
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr --build=aarch64-unknown-linux-gnu && \
    make && make install && \
    cd .. && rm -rf ta-lib*

# Set environment variable for Python to not buffer output (useful for logs)
ENV PYTHONUNBUFFERED=1

# Upgrade pip and install Poetry
RUN pip install --upgrade pip && pip install poetry==1.8.5

# Set working directory for the application
WORKDIR /app

# Copy dependency files (to take advantage of Docker cache during builds)
COPY pyproject.toml poetry.lock /app/
# Install pre-required pip packages to avoid timeouts
RUN pip install wcwidth mistune

# Copy the entire project, including the tools directory
COPY . /app/

# Pre-install large packages to avoid timeout during installation
RUN pip install numpy widgetsnbextension

# Install project dependencies with Poetry (avoid virtualenvs in the container)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Expose the application port
EXPOSE 80

# Run the application using Gunicorn
CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "src.api:app"]
