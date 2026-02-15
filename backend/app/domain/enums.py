"""Domain enumerations."""
from enum import Enum


class TaskStatus(str, Enum):
    """Task status values."""
    TODO = "TODO"
    DOING = "DOING"
    DONE = "DONE"
    BLOCKED = "BLOCKED"


class TaskSource(str, Enum):
    """Task creation source."""
    MANUAL_COMMAND = "MANUAL_COMMAND"
    CHAT_MESSAGE = "CHAT_MESSAGE"
