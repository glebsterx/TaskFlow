# Repository Contracts

Repository слой изолирует SQLite от бизнес-логики.

## TaskRepository

Методы:

create(task) -> Task

get_by_id(task_id) -> Task | None

list_all() -> list[Task]

list_by_status(status) -> list[Task]

list_week_tasks() -> list[Task]

update_status(task_id, status)

update(task)

delete(task_id)

---

## BlockerRepository

create(blocker) -> Blocker

list_by_task(task_id) -> list[Blocker]

list_active() -> list[Blocker]

---

## MeetingRepository

create(meeting) -> Meeting

list_recent(limit) -> list[Meeting]
