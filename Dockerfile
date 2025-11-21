FROM python:3.12-slim AS builder

WORKDIR /home/user/app

RUN apt-get update && apt-get install -y libpq-dev && \
    apt-get install -y --no-install-recommends gcc python3-dev

RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    build-essential \
    && apt-get clean

# Set environment variables for GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN pip install fiona

RUN pip install poetry

COPY ./pyproject.toml pyproject.toml
COPY ./poetry.lock poetry.lock
COPY ./README.md README.md
COPY ./geoproject geoproject

RUN poetry config virtualenvs.in-project true && \
    poetry install --no-interaction --no-ansi

CMD ["poetry", "run", "uvicorn", "geoproject.main:app", "--host", "0.0.0.0", "--port", "8000"]
