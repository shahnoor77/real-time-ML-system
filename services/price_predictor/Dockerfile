FROM python:3.10-slim

# Set non-interactive mode for apt
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# System dependencies (minimal set)
RUN apt-get update && apt-get install -y \
    gcc build-essential python3-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.5

# Set working directory
WORKDIR /app

# Install ta-lib Python binding (includes prebuilt C lib)
RUN pip install numpy==1.26.4 ta-lib==0.4.30

# Copy pyproject and lock file first (for Docker layer caching)
COPY pyproject.toml poetry.lock /app/

# Install project dependencies (except your own package)
RUN poetry install --no-root

# Copy the rest of the application
COPY . /app

# Expose the application port
EXPOSE 80

# Default command to run your app
CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "src.api:app"]
