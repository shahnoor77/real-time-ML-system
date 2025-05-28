FROM python:3.10-slim

# Install build tools and dependencies for TA-Lib and Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make wget \
    build-essential \
    python3-dev \
    libssl-dev libffi-dev \
    gfortran \
    libopenblas-dev liblapack-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download and build TA-Lib C library
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Set environment variables so Python ta-lib can find the C library
ENV TA_LIBRARY_PATH=/usr/lib
ENV TA_INCLUDE_PATH=/usr/include
ENV PYTHONUNBUFFERED=1

# Install Poetry
RUN pip install poetry==1.8.5

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock /app/

# Copy any local path dependencies needed for poetry install
COPY tools /app/tools

# Install dependencies (no --with needed since ta-lib is no longer optional)
RUN poetry config virtualenvs.create false && \
    poetry install --no-root

# Copy the rest of the application
COPY . /app

# Expose the port your app runs on
EXPOSE 80

# Run the app with Gunicorn
CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "src.api:app"]
