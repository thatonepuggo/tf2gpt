import multiprocessing
from time import sleep
import os
import threading

from flask import Flask, render_template, session, request, url_for, redirect, send_from_directory
from flask_socketio import SocketIO, emit
from markupsafe import Markup

from gtts import gTTS
from dotenv import load_dotenv
from rcon.source import Client
import rcon
import replicate
from pygame import mixer
from pygame import _sdl2 as device

from conlog import ConLog
from config import *

load_dotenv()


socketio = SocketIO
app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading")

backstory = PROMPT

chat_memory = []
vb_support = True

# globals #
global client
global conlog
global game_running
global kill_switch

kill_switch = False
game_running = False

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
You: <your message here>"""

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
            "max_new_tokens": 128,
            "min_new_tokens": -1
        },
    )
    full = ''.join(message)
    if full.lower().startswith("you: "):
        full = full[5:]
    chat_memory.append(f"You: {full}")
    print(full)
    return full

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

mixer.pre_init(devicename = VBCABLE)
mixer.init()

if not VBCABLE in device.audio.get_audio_device_names(False):
    print("To use voice-related AI commands, please get Virtual Audio Cable: https://vb-audio.com/Cable/.")
    vb_support = False
else:
    print("Virtual Audio Cable found. vb commands enabled!")

mixer.quit()

def is_command(message, cmd):
    return message.lower().startswith(f"{PREFIX}{cmd}")

def vb_command(message, cmd):
    if not vb_support and is_command(message, cmd):
        print("support")
    return vb_support and is_command(message, cmd)

def _quick_play(devicename, file):
    mixer.pre_init(devicename=devicename)
    mixer.init()
    mixer.music.load(file)
    mixer.music.play()
    while mixer.music.get_busy():
        if kill_switch:
            mixer.stop()
        pass
    mixer.quit()
    
def play_audio(file):
    inp = multiprocessing.Process(target=_quick_play, args=[VBCABLE, file]) 
    out = multiprocessing.Process(target=_quick_play, args=[SOUNDOUTPUT, file]) 
    
    inp.start() 
    out.start() 
    
    inp.join()
    out.join()

def tts(client: Client, text):
    tts = gTTS(text=text, lang='en', tld="co.uk", slow=False)
    try:
        os.remove(CACHED_SND)
    except FileNotFoundError:
        print("file does not exist, skipping removal.")
    tts.save(CACHED_SND)
    
    client.run('+voicerecord')
    play_audio(CACHED_SND)
    #mixer.music.load(CACHED_SND)
    #sleep(0.1)
    #mixer.music.play()
    #while mixer.music.get_busy():
    #    pass
    #mixer.quit()
    #mixer.init(devicename = VBCABLE)
    client.run('-voicerecord')

def ttsask(client: Client, username, args):
    tts(client, ask(username, ' '.join(args[1:])))
    
def ttssay(client: Client, args):
    tts(client, ' '.join(args[1:]))
    
def check_commands(client: Client, message: str, username: str = USERNAME):
    if kill_switch:
        return
    args = message.split(' ')
    #if is_command(message, "ask"):
    #    print("processing...")
    #    response = ask(username, message)
    #    print(response)
    #    for chunk in chunkstring(response, 127):
    #        client.run('say', chunk)
    #        sleep(1)
    if is_command(message, "backstory"):
        print(len(args))
        print(args)
        if len(args) < 1:
            print("ignored command. too few args")
            return
        backstory = ' '.join(args[1:])
        client.run('say', f"[tf2gpt] set backstory to '{backstory}'")
        if args[1] == "default":
            backstory = PROMPT
    elif vb_command(message, "ttsask"):
        ttsask(client, username, args)
    elif vb_command(message, "ttssay"):
        ttssay(client, args)

@app.route("/")
def home():
    if not game_running:
        return render_template('err.html', error="game_not_running")
    return render_template('index.html', refreshTime=REFRESH_TIME, killSwitch=str(kill_switch).lower())

@socketio.on("send_cmd")
def send_cmd(data: dict):
    print(data)
    message = data.get('message', '').strip()
    cmd_type = data.get('type', '').strip()
    if message == '':
        print('message is empty')
        return
    if cmd_type not in ['ai', 'rcon']:
        print('incorrect type')
        return
    
    if cmd_type == "ai":
        check_commands(client, message)
    elif cmd_type == "rcon":
        client.run(message)

@socketio.on("set_killswitch")
def set_killswitch(val: bool):
    print(f"KILLSWITCH: {val}")
    global kill_switch
    kill_switch = val

def run_rcon_thread():
    global game_running
    global client
    while True:
        try:
            with Client('127.0.0.1', 27015, passwd=PASSWORD) as client:
                conlog = ConLog(game_root=GAMEROOT, mod_root=MODROOT)
                while True:
                    escaped_log = str(Markup.escape(conlog.read())).replace("\n", "<br>")
                    socketio.emit("consoleget", escaped_log)
                    
                    new = conlog.readnewlines()

                    for line in new:
                        username_match = re_username.search(line)
                        message_match = re_message.search(line)

                        if username_match and message_match:
                            username = username_match.group()
                            message = message_match.group().lstrip()
                            check_commands(client, message, username)
                    sleep(REFRESH_TIME)
        except CONNECT_EXCEPTIONS:
            pass

def run_rcon_try_thread():
    global game_running
    while True:
        try:
            with Client('127.0.0.1', 27015, passwd=PASSWORD) as try_client:
                game_running = True
        except CONNECT_EXCEPTIONS:
            game_running = False
        sleep(CONNECTION_CHECK_TIME)

if __name__ == '__main__':
    rcon_thread = threading.Thread(target=run_rcon_thread)
    rcon_thread.start()
    rcon_try_thread = threading.Thread(target=run_rcon_try_thread)
    rcon_try_thread.start()
    socketio.run(app, use_reloader=False)