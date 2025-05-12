FROM python:3.10.3-slim-buster

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential wget gcc make \
    libffi-dev libssl-dev python3-dev \
    libopenblas-dev liblapack-dev gfortran \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install TA-Lib C library (v0.4.0)
RUN wget https://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz/download -O ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && cd ta-lib && \
    ./configure --prefix=/usr && make && make install && \
    cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Set library path
ENV LD_LIBRARY_PATH="/usr/lib"

# Install Poetry
RUN pip install poetry==1.8.5

# Set working directory
WORKDIR /app

# Add pyproject and lock first to cache dependencies
COPY pyproject.toml poetry.lock ./

# Use system TA-Lib and install ta-lib with no build isolation
RUN poetry config virtualenvs.create false && \
    poetry run pip install --no-build-isolation --no-cache-dir ta-lib==0.4.0 && \
    poetry install --no-root

# Copy source code
COPY . .

# Expose port
EXPOSE 80

# Run service
CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "src.api:app"]
