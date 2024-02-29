from rcon import Client
from config import *
from typing import Callable
from config import ConfigFile

conf = ConfigFile()

class AICommand:
    name: str
    aliases: list[str]
    func: Callable
    voice: bool
    min_args: int
    
    def __init__(self, name: str, func: Callable, voice = False, min_args = 0, aliases: list[str] = []):
        self.name = name
        self.func = func
        self.voice = voice
        self.min_args = min_args
        self.aliases = aliases
    
    # singular check for a name
    def _is_check(self, message, cmdname):
        return message.lower().split(' ')[0] == f"{conf.data["prefix"]}{cmdname}"
    
    def is_command(self, message):
        # check the main name
        if self._is_check(message, self.name):
            return True
        # check the aliases
        for alias in self.aliases:
            if self._is_check(message, alias):
                return True
        return False
            
    
    def exec(self, client: Client, username: str = conf.data["username"], message: str = ""):
        args = message.split(' ')
        if len(args) >= self.min_args:
            return self.func(client, username, message, args)
        return False