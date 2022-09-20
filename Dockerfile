FROM python:3.10-buster

RUN mkdir /app

WORKDIR /app
ENV PYTHONPATH=${PYTHONPATH}:${PWD} 

RUN pip3 install poetry
# RUN poetry config virtualenvs.create false

COPY pyproject.toml /app
COPY poetry.lock /app


COPY /src /app/src

RUN poetry install --without dev


CMD poetry run server