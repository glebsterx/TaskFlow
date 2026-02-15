# Error Handling

## Уровни ошибок

DomainError — ошибка бизнес-логики  
RepositoryError — ошибка базы  
TransportError — ошибка Telegram/Web

## Правила

- сервисы не выбрасывают SQLite исключения наружу
- пользователю показываются безопасные сообщения
- ошибки логируются
