FROM python:3.10.3-slim-buster

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc gfortran wget build-essential \
    python3-dev libssl-dev libffi-dev \
    ca-certificates libopenblas-dev liblapack-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install TA-Lib (required for ta-lib Python bindings)
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && rm -rf ta-lib*


# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    JUPYTER_PLATFORM_DIRS=1


# Install Poetry
RUN pip install poetry==1.8.5

# Set Poetry to use system environment
RUN poetry config virtualenvs.create false

# Set working directory
WORKDIR /app

# Copy only pyproject.toml and poetry.lock first for caching
COPY pyproject.toml poetry.lock /app/

# Copy tools dependency with its own pyproject.toml
COPY tools /app/tools

# Install dependencies
RUN poetry install --no-root

# Copy the rest of the project
COPY . /app

# Expose app port
EXPOSE 80

# Run the service
CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "src.api:app"]
