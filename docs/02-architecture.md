# System Architecture

## Высокоуровневая схема

Telegram Chat → Telegram Bot → Application Services → Repository → SQLite → Web API → Web UI

## Компоненты

### Telegram Bot
Обрабатывает команды, сообщения и inline действия.

### Application Layer
Содержит бизнес-логику работы с задачами.

### Repository Layer
Отвечает за доступ к SQLite.

### Web API
Read-only HTTP интерфейс для отображения данных.

### Web UI
HTML интерфейс поверх API.

## Архитектурные принципы

- единый источник истины — база
- бизнес-логика не зависит от Telegram
- Web и Bot используют один сервисный слой
- минимальная инфраструктура
