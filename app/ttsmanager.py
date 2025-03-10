# stdlib #
import os

# pypi #
from gtts import gTTS
from sty import fg, bg, ef, rs


# local #
from . import state
from . import config
from . import util
from . import soundplayer


last_text = ""


def tts(text: str, print_text=False):
  if util.is_empty(text):
    print(f"{fg.yellow}Empty TTS message: '{text}'.{fg.rs}")
    return

  global last_text
  if text != last_text:
    # translate the text
    translated_text = util.substitute_words(
        text, config.data["tts_translations"].get("words", {}))

    try:
      tts = gTTS(text=translated_text, lang='en',
                 tld=config.data["gtts_tld"], slow=False)
      try:
        os.remove(config.data["cached_snd"])
      except (FileNotFoundError, PermissionError):
        print(f"{fg.yellow}some errro, skipping removal.{rs.all}")

      tts.save(config.data["cached_snd"])
      last_text = text
    except AssertionError as e:
      print(f"{fg.red}gTTS shit itself: {e}{rs.all}")
  else:
    print(f"{fg.red}using cached sound{rs.all}")

  if print_text:
    print(f"{fg.green}{text}{fg.rs}\n")

  soundplayer.sp.play(config.data["cached_snd"])
