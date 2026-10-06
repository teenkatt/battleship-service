FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /service

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini pyproject.toml ./
COPY alembic ./alembic
COPY battleship ./battleship
COPY arena ./arena
COPY tests ./tests

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn battleship.main:app --host 0.0.0.0 --port 8000"]
