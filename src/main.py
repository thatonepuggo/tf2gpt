from time import sleep
import re

from dotenv import load_dotenv
from rcon.source import Client
import replicate

from conlog import ConLog

load_dotenv()

re_username = re.compile(r'.*(?= :)')
re_message = re.compile(r'(?<=. : ).*')

## EDIT THIS !! ##
GAMEROOT = "S:/SteamLibrary/steamapps/common/Team Fortress 2"
MODROOT = "tf"
PASSWORD = "dontcarelol"

PREFIX = ';'
PROMPT = "You are Jason Grant, the deathmatch mercenary from Open Fortress, an orphan raised on the silver screen with an affinity for heavier-weight women. " \
"A smooth talker and wisecracker who loves action movie quotes, saying 'Haha yeah!' and 'Frickin' awesome! " \
"Your best friend is the Civilian, a rich and portly British oil baron. Your girlfriend is Vivian, a fat secretary. You have a pet albino rat named Chuck." \
"A friend from long ago, Merv, is the one who introduced you to the world of deathmatch. " \
"He taught you most of what you know now, how to protect yourself in a fight, as well as your one-liners. "

backstory = PROMPT

chat_memory = []

def ask(author, question):
    global chat_memory
    chat_memory = chat_memory[-20:]
    memory_string = '\n'.join(chat_memory)
    gen_prompt = f"""{backstory}
here is your current chat history, use this to remember context from earlier. (if 'You' said this, you said this. Otherwise, that was a user.).
this is for you to refrence as memory, not to use in chat. i.e. "oh yes, i remember you saying this some time ago." if it isn't acutally in history, dont say it.
---beginning of your chat history, use this as memory.---
{memory_string}
---end of your chat history---
---beginning of current chat message---
{author}: {question}
You: """

    chat_memory.append(f"{author}: {question}")
    print(gen_prompt)
    message = replicate.run(
        "meta/llama-2-70b-chat",
        input={
            "debug": False,
            "top_k": 50,
            "top_p": 1,
            "prompt": question,
            "temperature": 0.5,
            "system_prompt": gen_prompt,
            "max_new_tokens": 500,
            "min_new_tokens": -1
        },
    )

    for event in message:
        pass
        #print(f"{ctx.message.author} asked: {question}")
        #print("output: " + str(event), end="")

    #embed=discord.Embed(title="Message", description=''.join(message), color=0x8300b3)
    #await ctx.send(embed=embed)
    chat_memory.append(f"You: {''.join(message)}")
    return ''.join(message)

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

with Client('127.0.0.1', 27015, passwd=PASSWORD) as client:
    conlog = ConLog(game_root=GAMEROOT, mod_root=MODROOT)
    
    while True:
        new = conlog.readnewlines()
        
        for line in new:
            username_match = re_username.search(line)
            message_match = re_message.search(line)
            if username_match and message_match:
                username = username_match.group()
                message = message_match.group().lstrip()
                
                if message.lower().startswith(f"{PREFIX}ask"):
                    print("processing...")
                    for chunk in chunkstring(ask(username, message), 128):
                        client.run('say', chunk)
                        sleep(1)
        sleep(5)
