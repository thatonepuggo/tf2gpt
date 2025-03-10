# stdlib #
import re
from time import sleep
from rcon.source import Client
from uuid import uuid4

# local #
from .config import config
from . import util
from . import state


class ConLog:
  """
  periodically checks the console.log file for changes.
  """
  logfile: str
  unread: int = 0

  BEGIN_STATUS = "__begin_status_output__"
  END_STATUS = "__end_status_output__"

  def __init__(self, logfile):
    self.logfile = logfile
    self.unread = 0
    self.readnewlines()  # set the unread to the newest line
    self.read()

  def open(self):
    return open(self.logfile, encoding="utf-8", errors='replace')

  def read(self):
    try:
      with self.open() as log:
        return log.read()
    except FileNotFoundError:
      return ""

  def readline(self, _hint=-1):
    try:
      with self.open() as log:
        return log.readline(_hint)
    except FileNotFoundError:
      return ""

  def readlines(self, _hint=-1):
    try:
      with self.open() as log:
        return log.readlines(_hint)
    except FileNotFoundError:
      return ""

  def readnewlines(self):
    contents = self.readlines()
    unread = self.unread
    self.unread = len(contents)
    return contents[unread:]

  def get_status(self):
    """
    get the server status so the AI can use it in its responses.
    """

    """
    it seems to work. i don't know if some tf2 update
    made the status command have a return value instead
    of just printing to the console, or this is just a linux
    thing, but oh well.
    """
    # uuid = str(uuid4())
    # begin_text = f"{self.BEGIN_STATUS}:{uuid}"
    # end_text = f"{self.BEGIN_STATUS}:{uuid}"

    # state.client.run(f"echo {begin_text}")
    result = state.client.run("status")
    # if util.is_empty(result):
    #  state.client.run(f"echo {end_text}")
    #
    #  recording = False
    #  result = ""
    #  newlines = self.readnewlines()
    #
    #  for line in newlines:
    #    if line.strip() == begin_text:
    #      recording = True
    #    elif line.strip() == end_text:
    #      recording = False
    #    if recording:
    #      result += line + "\n"
    #
    #  print("str: " + result)
    return result
