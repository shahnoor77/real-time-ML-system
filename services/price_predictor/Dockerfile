FROM python:3.10.3-slim-buster

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    gfortran \
    wget \
    libffi-dev \
    libssl-dev \
    python3-dev \
    libopenblas-dev \
    liblapack-dev \
    ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install TA-Lib C library
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && cd ta-lib && \
    ./configure --prefix=/usr && make && make install && \
    cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Set environment variables for TA-Lib
ENV TA_LIBRARY_PATH=/usr/lib
ENV TA_INCLUDE_PATH=/usr/include
ENV LD_LIBRARY_PATH="/usr/lib"
ENV PYTHONUNBUFFERED=1

# Install Poetry
RUN pip install poetry==1.8.5

# Set working directory
WORKDIR /app

# Pre-copy poetry files to leverage Docker caching
COPY pyproject.toml poetry.lock ./

# Pre-copy tools directory to install local dependency
COPY tools/ tools/

# Disable virtualenv creation and install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# Copy the rest of the application
COPY . .

# Expose the service port
EXPOSE 80

# Run the app with Gunicorn
CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "src.api:app"]
