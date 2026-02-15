# Telegram Integration

## Команды

### /task
Создание задачи через диалог.

### /week
Показ доски задач.

---

## Inline Actions

Формат callback:

task:{id}:start
task:{id}:done
task:{id}:block

---

## Обработка сообщений чата

Бот анализирует обычные сообщения.

Flow:

Message → Parser → Candidate → Confirmation → Task

---

## Требования к боту

- доступ к сообщениям
- inline клавиатуры
- отключён privacy mode для групп
