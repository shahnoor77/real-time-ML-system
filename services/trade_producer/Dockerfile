FROM python:3.10-slim

# Install Poetry
RUN pip install poetry==1.8.5

# Set workdir
WORKDIR /app

# Prevent Poetry from creating virtual environments
ENV POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH=/app

# Copy only project metadata first (for layer caching)
COPY pyproject.toml poetry.lock /app/

# Install dependencies globally in the container's Python environment
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-root

# Copy the rest of the application
COPY . /app/

# Run app using poetry (from global env)
CMD ["python", "src/main.py"]
