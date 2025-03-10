import re
import yaml


class ConfigFile:
  DEFAULTS = {
      "username": "System",
      "backstory_max_tts_len": 20,
      "log_max_lines": 250,
      "say_question_like_first_grader": False,

      "logfile": "C:/Program Files (x86)/Steam/steamapps/common/Team Fortress 2/console.log",
      "password": "dontcarelol",

      "prefix": "\\",

      "aliases": {},

      "backstory": """You are Jason Grant, the deathmatch mercenary from Open Fortress, an orphan raised on the silver screen with an affinity for heavier-weight women.
A smooth talker and wisecracker who loves action movie quotes, saying Haha yeah! and Frickin awesome!
Your best friend is the Civilian, a rich and portly British oil baron. Your girlfriend is Vivian, a fat secretary. You have a pet albino rat named Chuck.
A friend from long ago, Merv, is the one who introduced you to the world of deathmatch.
He taught you most of what you know now, how to protect yourself in a fight, as well as your one-liners.""",

      "vbcable": "CABLE Input (VB-Audio Virtual Cable)",
      "soundoutput": "Headset Earphone (HyperX Virtual Surround Sound)",

      "processing_snd": "processing.mp3",
      "cached_snd": "output.mp3",
      "gtts_tld": "co.uk",

      "tts_translations": {
          "words": {
              "?": "question mark",
              "!": "exclamation mark",
              ",": "comma",
              ".": "dot",
              ";": "semicolon",
              ":": "colon",
              "|": "pipe",
              "\u1e9e": "es zett",
              "\u00df": "es zett",
          }
      },

      "blocked_words": [],
      "blocked_words_deal_method": "ignore",
      "blocked_words_replacement": "bleep",
  }

  def __init__(self, config_file: str = "config.yaml"):
    self.config_file = config_file
    with open(self.config_file, "r") as conf:
      self._config = yaml.load(conf, yaml.Loader)

  @property
  def data(self) -> dict:
    ret = self._config
    if not isinstance(ret, dict):
      return self.DEFAULTS
    ret = self.DEFAULTS | ret
    return ret

  @property
  def keys_regex(self):
    """
    a regex that matches all of the keys in the DEFAULTS list.
    """
    keys = list(self.DEFAULTS.keys())
    keys = [re.escape(key) for key in keys]
    return f"({"|".join(keys)})"

  @property
  def version(self) -> int:
    """
    returns the config version (config.data["v"].)
    before v: 2, there was no 'v' key. therefore, if the config does not contain the 'v' key, it will default to 1.
    """
    ver = self.data.get("v", None)
    if not ver:
      return 1
    return ver


config = ConfigFile()
