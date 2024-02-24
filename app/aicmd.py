from rcon import Client
from config import *
from typing import Callable

class AICommand:
    name: str
    func: Callable
    voice: bool
    min_args: int
    
    def __init__(self, name: str, func: Callable, voice = False, min_args = 0):
        self.name = name
        self.func = func
        self.voice = voice
        self.min_args = min_args
    
    def is_command(self, message):
        return message.lower().split(' ')[0] == f"{PREFIX}{self.name}"
    
    def exec(self, client: Client, username: str = USERNAME, message: str = ""):
        args = message.split(' ')
        if len(args) >= self.min_args:
            return self.func(client, username, message, args)
        return False