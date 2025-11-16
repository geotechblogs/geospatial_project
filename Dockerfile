FROM python:3.12-slim AS builder

WORKDIR /home/user/app

RUN pip install poetry

COPY ./pyproject.toml pyproject.toml
COPY ./poetry.lock poetry.lock
COPY ./README.md README.md
COPY ./geoproject geoproject

RUN poetry config virtualenvs.in-project true && \
    poetry install --no-interaction --no-ansi
