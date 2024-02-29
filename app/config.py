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
    
    @property
    def data(self):
        with open(self.config_file, 'r') as conf:
            ret = yaml.load(conf, yaml.Loader)
        if type(ret) != dict:
            return self.DEFAULTS
        ret = self.DEFAULTS | ret
        return ret