FROM python:3.10.3-slim-buster

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential wget gcc make \
    libffi-dev libssl-dev python3-dev \
    libopenblas-dev liblapack-dev gfortran \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install TA-Lib C library (only 0.4.0 is available)
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz -O ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && cd ta-lib && \
    ./configure --prefix=/usr && make && make install && \
    cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Set environment variables for TA-Lib
ENV TA_LIBRARY_PATH=/usr/lib
ENV TA_INCLUDE_PATH=/usr/include
ENV LD_LIBRARY_PATH="/usr/lib"

# Install Poetry
RUN pip install poetry==1.8.5

# Set working directory
WORKDIR /app

# Copy pyproject and lock files first (to leverage Docker layer caching)
COPY pyproject.toml poetry.lock ./

# Copy local dependency (tools) directory before installing dependencies
COPY tools/ tools/

# Install Python dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-root

# Copy full source code (including src/)
COPY . .

# Expose service port
EXPOSE 80

# Run the service using gunicorn
CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "src.api:app"]
