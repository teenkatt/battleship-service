# Морской бой

REST-сервис игры в морской бой: FastAPI, PostgreSQL, Alembic.
Контракт API — [contract.md](contract.md).

## Запуск приложения

```
cp .env.example .env
docker compose up --build -d
```

## Запуск тестов

```
docker compose exec app python -m pytest -v
```

## Документация API (Swagger)

http://localhost:8000/docs
