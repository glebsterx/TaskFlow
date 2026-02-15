# Database Schema (SQLite)

## tasks

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    assignee_name TEXT,
    assignee_telegram_id INTEGER,
    status TEXT NOT NULL,
    due_date TEXT,
    definition_of_done TEXT,
    source TEXT NOT NULL,
    source_message_id INTEGER,
    source_chat_id INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

---

## blockers

CREATE TABLE blockers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_by INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY(task_id) REFERENCES tasks(id)
);

---

## meetings

CREATE TABLE meetings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_date TEXT NOT NULL,
    summary TEXT NOT NULL,
    created_at TEXT NOT NULL
);
