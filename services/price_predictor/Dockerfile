FROM python:3.10.3-slim-buster

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc wget build-essential \
    python3-dev libssl-dev libffi-dev \
    ca-certificates \
    gfortran libopenblas-dev liblapack-dev \
    libta-lib0 libta-lib0-dev

# Download and install TA-Lib C library (0.4.0)
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib*

# Environment setup
ENV PYTHONUNBUFFERED=1

# Install poetry
RUN pip install poetry==1.8.5

WORKDIR /app

# Install ta-lib Python bindings separately before using poetry
RUN pip install numpy==1.26.4 && pip install ta-lib==0.4.0

# Copy project files
COPY pyproject.toml poetry.lock /app/
COPY tools /app/tools

# Now let Poetry install the rest of the dependencies
RUN poetry install --no-root

COPY . /app

EXPOSE 80

CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "src.api:app"]
