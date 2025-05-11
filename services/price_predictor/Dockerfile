# Use a specific Python version image
FROM python:3.10.3-slim-buster

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc gfortran wget build-essential \
    python3-dev libssl-dev libffi-dev \
    ca-certificates libopenblas-dev liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Install TA-Lib C library
RUN wget -q http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && make && make install && \
    cd .. && rm -rf ta-lib*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    JUPYTER_PLATFORM_DIRS=1 \
    LD_LIBRARY_PATH=/usr/lib

# Install Poetry
RUN pip install poetry==1.8.5

# Disable Poetry's virtual environment creation
RUN poetry config virtualenvs.create false

# Set working directory in the container
WORKDIR /app

# Copy Poetry configuration files first for better cache efficiency
COPY pyproject.toml poetry.lock /app/

# Copy tools directory (if needed for installation or as a source)
COPY tools /app/tools

# Install dependencies using Poetry
RUN poetry install --no-root --no-interaction --no-ansi

# Copy the rest of the application source code
COPY . /app/

# Expose the application port (default for Gunicorn)
EXPOSE 80

# Set the default command to start Gunicorn with Poetry
CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "src.api:app"]
