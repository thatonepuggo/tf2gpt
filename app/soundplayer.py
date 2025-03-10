# stdlib #
import sys
from typing import Self
from os import environ

# pypi #
import pulsectl

# local #
from .util import parse_pa_modargs

# needed otherwise pygame wont recognize sources/sinks
if sys.platform == "linux":
  environ["SDL_AUDIODRIVER"] = "pulseaudio"

from pygame import mixer

# local #
from .consts import SINK_NAME, SOURCE_NAME, VBCABLE_NAME
from . import state

sink_id: int
source_id: int


class SoundPlayer:

  kill_switch: bool = False
  auto_disable_voice: bool = True

  def __init__(self):
    if sys.platform == "linux":
      with pulsectl.Pulse("tf2gpt") as pulse:
        global sink_id
        global source_id

        self._clear_modules(pulse)

        # "speakers"
        sink_id = pulse.module_load(
            "module-null-sink", f"sink_name={SINK_NAME}")

        # "mic"
        source_id = pulse.module_load(
            "module-virtual-source", f"source_name={SOURCE_NAME} master={SINK_NAME}.monitor")

        print(sink_id, source_id)

  def _clear_modules(self, pulse: pulsectl.Pulse):
    for module in pulse.module_list():
      try:
        modargs = parse_pa_modargs(module.argument)
        if (module.name == "module-virtual-source" and modargs.get("source_name", "") == SOURCE_NAME) \
                or (module.name == "module-null-sink" and modargs.get("sink_name", "") == SINK_NAME):
          pulse.module_unload(module.index)
      except AttributeError:
        pass

  def play(self, filename: str):
    state.client.run("+voicerecord")

    if sys.platform == "win32":
      mixer.init(devicename=VBCABLE_NAME)
    elif sys.platform == "linux":
      mixer.init(devicename=f"{SINK_NAME} Audio/Sink sink")

    mixer.music.load(filename)
    mixer.music.play()
    while mixer.music.get_busy():  # wait for audio to finish playing
      if self.kill_switch:
        mixer.music.stop()

    if self.auto_disable_voice:
      state.client.run("-voicerecord")

  def close(self):
    if sys.platform == "linux":
      with pulsectl.Pulse("tf2gpt") as pulse:
        global sink_id
        global source_id
        pulse.module_unload(sink_id)
        pulse.module_unload(source_id)

  def __enter__(self) -> Self:
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.close()


sp: SoundPlayer = None
