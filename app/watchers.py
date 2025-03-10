# stdlib #
from typing import Any, Optional, Protocol
from collections.abc import Callable

# pypi #
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, FileSystemEvent, EVENT_TYPE_OPENED, EVENT_TYPE_CLOSED, EVENT_TYPE_CLOSED_NO_WRITE

# local #
from .util import ignore_simple


WatcherCallback = Callable[[Optional[FileSystemEvent]], Any]


class CallbackWatcherEventHandler(PatternMatchingEventHandler):
  callback: WatcherCallback

  def on_any_event(self, event: FileSystemEvent):
    if event.event_type in [EVENT_TYPE_OPENED, EVENT_TYPE_CLOSED, EVENT_TYPE_CLOSED_NO_WRITE]:
      return

    ignore_simple(self.callback)(event)


class CallbackWatcher:
  """
  the file path to watch. can use globs.
  """
  watch_file: str

  """
  the callback function.
  """
  callback: WatcherCallback

  def __init__(self, watch_file: str, callback: WatcherCallback):
    self.watch_file = watch_file
    self.callback = callback

    self.observer = Observer()

  def run(self):
    self.event_handler = CallbackWatcherEventHandler()
    self.event_handler.callback = self.callback
    self.observer.schedule(self.event_handler, self.watch_file, recursive=True)
    self.observer.start()
    try:
      while True:
        pass
    except:
      self.observer.stop()

    self.observer.join()
