FROM python:3.10.3-slim-buster

# stream output to console
ENV PYTHONUNBUFFERED=1

# install poetry inside the container
RUN pip install poetry==1.8.5

WORKDIR /app

# copy the pyproject.toml and poetry.lock files into the container
COPY pyproject.toml poetry.lock /app/

# copy all the source code into the container
# COPY src/*.py /app/src/
COPY . /app/

# install Python dependencies from the pyproject.toml file
RUN poetry install --no-root

# Config the virtualenvs in-project
RUN poetry config virtualenvs.in-project true

# Force the creation of a new virtualenv and install the dependencies
RUN poetry run pip install --upgrade pip
RUN poetry install

CMD ["poetry", "run", "python", "src/main.py"]