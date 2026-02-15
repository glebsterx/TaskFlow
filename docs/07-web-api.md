# Web API

Base URL: /api

## GET /tasks

Query параметры:

- status
- assignee

Response:

[
  {
    "id": 1,
    "title": "...",
    "assignee_name": "...",
    "status": "DOING",
    "due_date": "2026-02-20"
  }
]

---

## GET /board

Response:

{
  "TODO": [],
  "DOING": [],
  "BLOCKED": [],
  "DONE": []
}

---

## GET /blockers

Response:

[
  {
    "task_id": 1,
    "task_title": "...",
    "text": "..."
  }
]

---

## GET /meetings

Response:

[
  {
    "date": "2026-02-10",
    "summary": "..."
  }
]
