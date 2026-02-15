# Callback Data Protocol

Формат callback_data:

entity:entity_id:action

## Task Actions

task:{id}:start
task:{id}:done
task:{id}:block

## Message Candidate

candidate:confirm:{message_id}
candidate:reject:{message_id}
