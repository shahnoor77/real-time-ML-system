FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc build-essential wget \
    python3-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install TA-Lib C library (0.4.0)
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && make install && \
    cd .. && rm -rf ta-lib*

# Install Poetry
RUN pip install poetry==1.8.5

WORKDIR /app

# ✅ Install numpy (compatible version) and ta-lib
RUN pip install numpy==1.23.5 ta-lib==0.4.30

# Copy pyproject and poetry.lock (cached layer)
COPY pyproject.toml poetry.lock /app/

# Install other dependencies
RUN poetry install --no-root

# Copy application files
COPY . /app

EXPOSE 80

CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "src.api:app"]
