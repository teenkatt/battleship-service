# Battleship service

Игровой сервис для турнира по морскому бою. Контракт API — [CONTRACT.md](CONTRACT.md).

Сейчас реализована ручка `POST /game` (начать игру) и служебная `GET /ping`; остальные ручки контракта пока не реализованы.

## Как поднять

1. `cp .env.example .env`
2. `docker compose up -d --build`

Сервис слушает порт 8000, миграции применяются при старте контейнера `api`.

## Как проверить

- тесты: `docker compose exec api pytest`
- документация API: http://localhost:8000/docs
- остановить: `docker compose down`
