FROM python:3.10.3-slim-buster

# Install required system packages
RUN apt-get update && apt-get install -y \
    gcc wget build-essential \
    python3-dev libssl-dev libffi-dev \
    ca-certificates gfortran \
    libopenblas-dev liblapack-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Download and install TA-Lib 0.4.0 from SourceForge
RUN wget https://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz/download -O ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Ensure Python output is shown in logs
ENV PYTHONUNBUFFERED=1

# Install Poetry
RUN pip install poetry==1.8.5

# Set working directory
WORKDIR /app

# Copy dependency files and install Python dependencies
COPY pyproject.toml poetry.lock /app/
COPY tools /app/tools
RUN poetry config virtualenvs.create false && poetry install --no-root

# Copy the rest of the source code
COPY . /app

# Expose application port
EXPOSE 80

# Run the application using Gunicorn
CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "src.api:app"]
