import re
from config import config
from rcon.source import Client

class ConLog:
    """
    con_logfile: the value of the con_logfile convar.
    game_root: root of the game (e.x. team fortress 2 = C:/Program Files (x86)/Steam/steamapps/common/Team Fortress 2)
    mod_root: name of the mod (e.x. team fortress 2 = tf)
    """
    con_logfile: str
    game_root: str
    mod_root: str
    unread: int
    
    def __init__(self,
                 con_logfile: str = "console.log",
                 game_root: str = config.data["gameroot"], 
                 mod_root: str = config.data["modroot"]):
        self.con_logfile = con_logfile
        self.game_root = game_root
        self.mod_root = mod_root
        self.unread = 0
        self.readnewlines() # set the unread to the newest line
        self.read()
    
    @property
    def logfile(self):
        return f"{self.game_root}/{self.mod_root}/{self.con_logfile}"

    def open(self):
        return open(self.logfile, encoding="utf-8")

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
        
    
    def status(self, client: Client):
        # dont ask what this does (because idk)
        # its from here: https://github.com/MegaAntiCheat/client-backend/blob/41bfd62d9c46158677b6e0b250c0234cb4a935e7/src/io/regexes.rs#L127C8-L127C88
        REGEX_STATUS = re.compile(r'^#\s*(\d+)\s"(.*)"\s+(\[U:\d:\d+\])\s+((?:[\ds]+:?)+)\s+(\d+)\s*(\d+)\s*(\w+).*$')
        
        client.run("status")
        lines = self.readnewlines()
        
        status_lines = []
        for line in lines:
            if REGEX_STATUS.match(line):
                status_lines.append(line)
        
        return status_lines