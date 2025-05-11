# Use a Debian-based slim Python image
FROM python:3.10.3-slim-buster

# Install build tools and TA-Lib dependencies
RUN apt-get update && apt-get install -y \
    gcc wget build-essential \
    python3-dev libssl-dev libffi-dev \
    gfortran libopenblas-dev liblapack-dev \
    ca-certificates curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Download and build TA-Lib from source
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && make install && \
    cd .. && rm -rf ta-lib*

# Set environment to ensure TA-Lib is found
ENV LD_LIBRARY_PATH="/usr/lib:$LD_LIBRARY_PATH"
ENV PYTHONUNBUFFERED=1

# Install Poetry
RUN pip install --upgrade pip && pip install poetry==1.8.2

# Set working directory
WORKDIR /app

# Copy dependency files first for Docker caching
COPY pyproject.toml poetry.lock /app/

# Pre-install packages prone to timeout in Quix
RUN pip install wcwidth mistune

# Install project dependencies (disables venvs for Docker)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy project files last to keep Docker caching efficient
COPY . /app/

# Expose app port (if Quix uses internal service discovery, this is optional)
EXPOSE 80

# Run your app with Gunicorn via Poetry
CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "src.api:app"]
