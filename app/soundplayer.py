from math import ceil

import threading
from time import sleep
import time
import vlc
from rcon.source import Client

from config import config
import numpy as np
import mutagen
from mutagen.mp3 import MP3 

DEFAULT_VOLUME = config.data["default_volume"]

class SoundPlayer:
    @staticmethod
    # Get list of output devices
    def get_device(player: vlc.MediaPlayer, devicename: str):
        mods = player.audio_output_device_enum()
        if mods:
            mod = mods
            while mod:
                mod = mod.contents
                # If device is found, return its module and device id
                if devicename in str(mod.description):
                    device = mod.device
                    module = mod.description
                    return device, module
                mod = mod.next

    def __init__(self, volume=DEFAULT_VOLUME):
        self.instance: vlc.Instance = vlc.Instance("--no-xlib -q")

        self.input_player: vlc.MediaPlayer = self.instance.media_player_new()
        self.output_player: vlc.MediaPlayer = self.instance.media_player_new()

        self.url = ""
        self.stopped = False
        self.paused = False
        self.volume = volume
        self.auto_disable_voice = True
        self.kill_switch = False
        self.length = 0

    def wait_until_done(
        self, client: Client, inp: threading.Thread, out: threading.Thread, length: int
    ):
        inp.join()
        out.join()
        sleep(length)
        self.stopped = True

        if self.auto_disable_voice:
            client.run("-voicerecord")

    def play(self, client: Client, file: str, block: bool = True):
        self.stopped = False
        self.url = file
        length = MP3(file).info.length

        print(f"{'blocking to ' if block else ''}start sound {file}")
        
        inp = None
        out = None
        
        if not self.kill_switch:
            client.run("+voicerecord")
            # play through the microphone
            inp = threading.Thread(
                target=self._quick_play,
                args=[self.input_player, config.data["vbcable"], file, 1],
                daemon=True,
            )

            # play through the speakers
            out = threading.Thread(
                target=self._quick_play,
                args=[self.output_player, config.data["soundoutput"], file, 1],
                daemon=True,
            )
            
            inp.start()
            out.start()
        
        wait_thread = threading.Thread(
            target=self.wait_until_done, args=[client, inp, out, length]
        )
        wait_thread.start()
        if block:
            wait_thread.join()

    @property
    def paused(self) -> bool:
        return self.stopped if self.stopped else self._paused

    @paused.setter
    def paused(self, val: bool):
        self._paused = val
        self.input_player.set_pause(val)
        self.output_player.set_pause(val)

    @property
    def playing(self) -> bool:
        return not self.paused

    @playing.setter
    def playing(self, val: bool):
        self.paused = not val

    def _quick_play(
        self, player: vlc.MediaPlayer, devicename: str, file: str, volume_mul=1
    ):
        device_id, _ = self.get_device(player, devicename)

        def _upd_volume():
            # multiply volume by volume multiplier
            # clamp volume between 0-100
            # round
            vol = ceil(np.clip(self.volume * volume_mul, 0, 100))
            player.audio_set_volume(vol)
            return vol

        player.audio_output_device_set(None, device_id)

        media: vlc.Media = self.instance.media_new(file)
        player.set_media(media)

        _upd_volume()
        player.play()