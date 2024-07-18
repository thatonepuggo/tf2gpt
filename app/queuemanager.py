class QueueItem:
    def __init__(self, username: str, message: str, is_system = False):
        self.username = username
        self.message = message
        self.is_system = is_system
    def __dict__(self):
        return {
            "username": self.username,
            "message": self.message,
            "is_system": self.is_system,
        }
queue: list[QueueItem] = []