# Telegram FSM Scenarios

## Создание задачи (/task)

State: WAIT_TITLE
User вводит название

State: WAIT_ASSIGNEE
User вводит имя или пропускает

State: WAIT_DUE_DATE
User вводит дату или пропускает

State: WAIT_DEFINITION
User вводит критерий готовности

State: CONFIRM
Показывается карточка задачи
Кнопки:
- создать
- отменить
