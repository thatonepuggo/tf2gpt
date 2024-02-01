class ConLog:
    """
    con_logfile: the value of the con_logfile convar.
    game_root: root of the game (e.x. team fortress 2 = C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2)
    mod_root: name of the mod (e.x. team fortress 2 = tf)
    """
    con_logfile: str
    game_root: str
    mod_root: str
    unread: int
    
    def __init__(self,
                 con_logfile: str = "console.log", 
                 game_root: str = "C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2", 
                 mod_root: str = "tf"):
        self.con_logfile = con_logfile
        self.game_root = game_root
        self.mod_root = mod_root
        self.unread = 0
        self.readnewlines() # set the unread to the newest line
        self.read()
    
    def open(self):
        return open(f"{self.game_root}/{self.mod_root}/{self.con_logfile}", encoding="utf_8")
    
    def read(self):
        with self.open() as log:
            return log.read()
    
    def readline(self, _hint = -1):
        with self.open() as log:
            return log.readline(_hint)
        
    def readlines(self, _hint = -1):
        with self.open() as log:
            return log.readlines(_hint)
    
    def readnewlines(self):
        contents = self.readlines()
        unread = self.unread
        self.unread = len(contents)
        return contents[unread:]
        
