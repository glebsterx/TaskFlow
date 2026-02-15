# Deployment

## Сервисы

- telegram bot
- web api

Оба используют одну SQLite базу.

## Docker запуск

docker compose up --build -d

## Персистентность

Данные хранятся в volume:

/data/teamflow.db
