# Use a Python 3.10 slim image as the base image
FROM python:3.10.3-slim-buster

# install gcc and python3-dev to compile Python packages
RUN apt-get update && apt-get install -y \
    gcc wget build-essential \
    python3-dev libssl-dev libffi-dev \
<<<<<<< HEAD
    gfortran libopenblas-dev liblapack-dev \
    ca-certificates curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install TA-Lib from source
=======
    ca-certificates

# Install additional libraries needed for scipy
RUN apt-get install -y gfortran libopenblas-dev liblapack-dev

# Download and install TA-Lib
>>>>>>> c5aeca9fe5f2144d75d3c815c735097c70b7dabc
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr --build=aarch64-unknown-linux-gnu && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib*

<<<<<<< HEAD
# Set environment variable for Python to not buffer output (useful for logs)
ENV PYTHONUNBUFFERED=1

# Upgrade pip and install Poetry
RUN pip install --upgrade pip && pip install poetry==1.8.5

# Set working directory for the application
WORKDIR /app

# Copy dependency files (to take advantage of Docker cache during builds)
=======
# stream output to console
ENV PYTHONUNBUFFERED=1

# install poetry inside the container
RUN pip install poetry==1.8.5

WORKDIR /app

# This line here is ugly as hell. Please don't do this.
# Overwriting the PYTHONPATH environment variable is a bad practice.
# add /app/src to PYTHONPATH
# ENV PYTHONPATH "${PYTHONPATH}:/app/src"

# copy the pyproject.toml and poetry.lock files into the container
>>>>>>> c5aeca9fe5f2144d75d3c815c735097c70b7dabc
COPY pyproject.toml poetry.lock /app/
# Install pre-required pip packages to avoid timeouts
RUN pip install wcwidth mistune

<<<<<<< HEAD
# Copy the entire project, including the tools directory
COPY . /app/

# Pre-install large packages to avoid timeout during installation
RUN pip install numpy widgetsnbextension

# Install project dependencies with Poetry (avoid virtualenvs in the container)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Expose the application port
EXPOSE 80

# Run the application using Gunicorn
CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "src.api:app"]
=======
# copy the tools directory into the container so that we can install it
COPY tools /app/tools

# install Python dependencies from the pyproject.toml file
RUN poetry install

# copy all the source code into the container and the README file
COPY . /app

# Expose the port that the application will run on
EXPOSE 80

# Command to run the application with Gunicorn
CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "src.api:app"]
>>>>>>> c5aeca9fe5f2144d75d3c815c735097c70b7dabc
