# Package Structure

Проект реализован как модульный монолит с разделением по слоям.

## Корневая структура

app/
├── main.py
├── config.py
├── bot.py
│
├── core/
│   ├── db.py
│   ├── logging.py
│   ├── clock.py
│   └── exceptions.py
│
├── domain/
│   ├── models.py
│   ├── enums.py
│   └── events.py
│
├── repositories/
│   ├── task_repository.py
│   ├── blocker_repository.py
│   └── meeting_repository.py
│
├── services/
│   ├── task_service.py
│   ├── board_service.py
│   └── message_parsing_service.py
│
├── telegram/
│   ├── handlers/
│   ├── keyboards/
│   └── fsm/
│
└── web/
    ├── app.py
    ├── routes.py
    ├── schemas.py
    └── templates/
