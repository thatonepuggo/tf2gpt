import yaml

class ConfigFile:
    DEFAULTS = {
        "username": "System",
        "backstory_max_len": 20,
        "log_max_lines": 250,
        "say_question_like_first_grader": False,
        
        "gameroot": "C:/Program Files (x86)/Steam/steamapps/common/Team Fortress 2",
        "modroot": "tf",
        "password": "dontcarelol",
        
        "prefix": "\\",
        "prompt": """You are Jason Grant, the deathmatch mercenary from Open Fortress, an orphan raised on the silver screen with an affinity for heavier-weight women.
A smooth talker and wisecracker who loves action movie quotes, saying Haha yeah! and Frickin awesome!
Your best friend is the Civilian, a rich and portly British oil baron. Your girlfriend is Vivian, a fat secretary. You have a pet albino rat named Chuck.
A friend from long ago, Merv, is the one who introduced you to the world of deathmatch.
He taught you most of what you know now, how to protect yourself in a fight, as well as your one-liners.""",
        
        "vbcable": "CABLE Input (VB-Audio Virtual Cable)",
        "soundoutput": "Headset Earphone (HyperX Virtual Surround Sound)",
        "default_volume": 100,
        
        "processing_snd": "processing.mp3",
        "cached_snd": "output.mp3",
         
        "refresh_time": 1,
        "connection_check_time": 5,
        
        "tts_translations": {
            "words": {
                "?": "question mark",
                "!": "exclamation mark",
                ",": "comma",
                ".": "dot",
                ";": "semicolon",
                ":": "colon",
                "|": "pipe",
                "ß": "es zett",
            }
        }
    }
    
    def __init__(self, config_file: str = "app/config.yaml"):
        self.config_file = config_file
        with open(self.config_file, "r") as conf:
            self._config = yaml.load(conf, yaml.Loader)

    @property
    def data(self):
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
        ret = []
        for key in self.DEFAULTS.keys():
            ret.append(key)
        return f"({"|".join(ret)})"

config = ConfigFile()