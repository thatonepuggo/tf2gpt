# stdlib #
from rcon import Client
from typing import Callable

# local #
from .config import config

# TODO: for non important commands like queuelength,
# there could be a "prioritize" bool  which sends it
# to the front of the queue. also a "clear_others" bool,
# to clear other instances of the command in the queue.


class AICommand:
  name: str
  aliases: list[str]
  func: Callable
  voice: bool
  min_args: int

  def __init__(self, name: str, func: Callable, voice=False, min_args=0, aliases: list[str] = []):
    self.name = name
    self.func = func
    self.voice = voice
    self.min_args = min_args
    self.aliases = aliases

  def _check_name(self, message: str, cmdname: str) -> bool:
    """
    check if a message matches a certain command name
    """
    return message.lower().split(' ')[0] == f"{config.data["prefix"]}{cmdname}"

  def matches(self, message):
    """
    check if a message matches this command's name or its aliases
    """
    config_aliases = config.data["aliases"].get(self.name, [])
    # check the main name, program aliases, and config aliases
    for alias in [self.name, *self.aliases, *config_aliases]:
      if self._check_name(message, alias):
        return True

    return False

  def exec(self, username: str = config.data["username"], message: str = ""):
    args = message.split(' ')
    if len(args) >= self.min_args:
      return self.func(username, message, args)
    return False
