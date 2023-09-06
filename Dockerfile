FROM python:3.10.11

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock* /app/

RUN pip install -U pip
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --no-root

COPY . /app

RUN chmod +x run.sh
ENV PYTHONPATH=/app

CMD ["./run.sh"]