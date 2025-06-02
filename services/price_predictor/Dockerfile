FROM python:3.10.3-slim-buster

RUN apt-get update && apt-get install -y \
    gcc wget build-essential \
    python3-dev libssl-dev libffi-dev \
    ca-certificates gfortran \
    libopenblas-dev liblapack-dev \
    curl

# Install TA-Lib C library
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && make install && \
    cd .. && rm -rf ta-lib*

ENV CFLAGS="-I/usr/include" \
    LDFLAGS="-L/usr/lib" \
    LD_LIBRARY_PATH="/usr/lib" \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_RETRIES=10 \
    POETRY_CACHE_DIR="/var/cache/pypoetry"

# Install Poetry
RUN pip install poetry==1.8.5

WORKDIR /app
COPY pyproject.toml poetry.lock /app/
COPY tools /app/tools
RUN poetry add ta-lib@^0.4.0
RUN poetry install

COPY . /app

EXPOSE 80
CMD ["poetry", "run", "gunicorn", "-w", "2", "-b", "0.0.0.0:80", "src.api:app"]
