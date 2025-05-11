FROM python:3.10.3-slim-buster

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc wget build-essential \
    python3-dev libssl-dev libffi-dev \
    gfortran libopenblas-dev liblapack-dev \
    ca-certificates curl && \
    apt-get clean

# Install TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr --build=aarch64-unknown-linux-gnu && \
    make && make install && \
    cd .. && rm -rf ta-lib*

# Avoid buffering Python output
ENV PYTHONUNBUFFERED=1

# Install Poetry
RUN pip install --upgrade pip && pip install poetry==1.8.5

# Set working directory
WORKDIR /app

# Copy dependency files first
COPY pyproject.toml poetry.lock /app/

# Copy local path dependencies (e.g. tools) before install
COPY tools /app/tools

# Pre-install large packages to avoid timeout
RUN pip install numpy widgetsnbextension

# Install project dependencies with Poetry
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi

# Copy the rest of the application source code
COPY . /app

# Expose application port
EXPOSE 80

# Run the app
CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "src.api:app"]
