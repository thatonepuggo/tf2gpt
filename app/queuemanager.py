from collections import deque


class QueueItem:
  def __init__(self, username: str, message: str, is_system: bool = False):
    self.username = username
    self.message = message
    self.is_system = is_system

  def __repr__(self):
    return f"<QueueItem {self.username=} {self.message=} {self.is_system=}>"

  def to_json(self):
    return {
        "username": self.username,
        "message": self.message,
        "is_system": self.is_system,
    }


queue: deque = deque()


def json_queue() -> list[dict]:
  return [item.to_json() for item in queue]
