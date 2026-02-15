# Domain Model

## Task

Центральная сущность системы.

### Поля

- id: integer
- title: string
- description: string | null
- assignee_name: string | null
- assignee_telegram_id: integer | null
- status: TaskStatus
- due_date: datetime | null
- definition_of_done: string | null
- source: TaskSource
- source_message_id: integer | null
- source_chat_id: integer | null
- created_at: datetime
- updated_at: datetime

### TaskStatus

- TODO
- DOING
- DONE
- BLOCKED

### TaskSource

- MANUAL_COMMAND
- CHAT_MESSAGE

---

## Blocker

Описание препятствия выполнения задачи.

Поля:

- id
- task_id
- text
- created_by
- created_at

---

## Meeting

Фиксация результатов встречи.

Поля:

- id
- meeting_date
- summary
- created_at

---

## MessageCandidate

Временная модель распознанной задачи из сообщения.

Поля:

- text
- detected_assignee
- detected_due_date
- confidence
