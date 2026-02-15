# Domain Events

События используются для логирования и будущего расширения.

В MVP события не публикуются во внешние системы.

## TaskCreated

Поля:
- task_id
- source
- created_at

## TaskStatusChanged

Поля:
- task_id
- old_status
- new_status
- changed_at

## BlockerAdded

Поля:
- task_id
- blocker_id
- created_at

## MeetingLogged

Поля:
- meeting_id
- created_at
