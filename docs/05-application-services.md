# Application Services

## TaskService

Основная бизнес-логика работы с задачами.

Методы:

- create_task
- update_status
- list_week_tasks
- list_tasks_by_status
- attach_blocker
- create_from_message

---

## MessageParsingService

Отвечает за распознавание задач из сообщений.

Методы:

- parse_message
- extract_assignee
- extract_due_date

---

## BoardService

Формирует доску состояния задач.

Методы:

- get_week_board
- group_tasks_by_status
