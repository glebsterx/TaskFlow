# Coding Standards

## Python

- Python 3.11+
- type hints обязательны
- async/await везде
- pydantic для DTO
- dataclasses для domain моделей

## Архитектура

- бизнес-логика только в services
- handlers не содержат логики
- repository только SQL

## Стиль

- один файл — одна ответственность
- явные зависимости
- без глобальных объектов
