FROM python:3.10-slim

# Install system dependencies, TA-Lib C library, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make \
    libta-lib0 libta-lib-dev \
    libssl-dev libffi-dev \
    gfortran \
    libopenblas-dev liblapack-dev \
    python3-dev \
    ca-certificates \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables so ta-lib is correctly found
ENV TA_LIBRARY_PATH=/usr/lib
ENV TA_INCLUDE_PATH=/usr/include
ENV LD_LIBRARY_PATH="/usr/lib:$LD_LIBRARY_PATH"
ENV PYTHONUNBUFFERED=1

# Install Poetry
RUN pip install poetry==1.8.5

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock /app/

# Copy local path dependencies needed for poetry install
COPY tools /app/tools

# Install dependencies
RUN poetry config virtualenvs.create false \
 && poetry install --no-root

# Copy the rest of the application
COPY . /app

# Expose app port
EXPOSE 80

# Run app using Gunicorn
CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "src.api:app"]
