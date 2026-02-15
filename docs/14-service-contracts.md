# Service Contracts

Application слой не знает о Telegram и HTTP.

## TaskService

create_task(
    title,
    assignee_name,
    due_date,
    definition_of_done,
    source
) -> Task

start_task(task_id)

complete_task(task_id)

block_task(task_id, text)

create_from_message(candidate)

---

## BoardService

get_board() -> dict[TaskStatus, list[Task]]

get_week_summary() -> BoardSummary

---

## MessageParsingService

parse_message(text) -> MessageCandidate | None
