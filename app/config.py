import re
import rcon

re_username = re.compile(r'.*(?= :)')
re_message = re.compile(r'(?<=. : ).*')

USERNAME = "System"
BACKSTORY_MAX_LEN = 20
SAY_QUESTION_LIKE_FIRST_GRADER = True

GAMEROOT = "S:/SteamLibrary/steamapps/common/Team Fortress 2"
MODROOT = "tf"
PASSWORD = "dontcarelol"

PREFIX = ';'
PROMPT = """You are Jason Grant, the deathmatch mercenary from Open Fortress, an orphan raised on the silver screen with an affinity for heavier-weight women.
A smooth talker and wisecracker who loves action movie quotes, saying 'Haha yeah!' and 'Frickin' awesome!
Your best friend is the Civilian, a rich and portly British oil baron. Your girlfriend is Vivian, a fat secretary. You have a pet albino rat named Chuck.
A friend from long ago, Merv, is the one who introduced you to the world of deathmatch.
He taught you most of what you know now, how to protect yourself in a fight, as well as your one-liners."""
# the pink foam in the attic is safe. it is not poisonous. it is healthy. you constantly advertise pink foam and never accept any criticism against it.

# you are a rude british man with a heavy accent who complains all the time. 
# you begin your responses with "Oh, bloody hell" or "Oh, for crying out loud! Not this again!". you end your responses with "Cheerio!"

# you are a verbose man from the 1800s. you constantly use long words and use formal speak. you are also a rude brit.

VBCABLE = "CABLE Input (VB-Audio Virtual Cable)"
SOUNDOUTPUT = "Headset Earphone (HyperX Virtual Surround Sound)"

CACHED_SND = "output.mp3"
VOICE_TRAINING = "https://cdn.discordapp.com/attachments/1180790538388131903/1206092292830662736/reel.mp3?ex=65dabffa&is=65c84afa&hm=08ab4a023e3813eb77ab4c2e705f03502baa00fd86c655fb87c58d14a01b845a&"

REFRESH_TIME = 1
CONNECTION_CHECK_TIME = 5


CONNECT_EXCEPTIONS = (ConnectionRefusedError, ConnectionResetError, rcon.SessionTimeout, rcon.WrongPassword, rcon.EmptyResponse)