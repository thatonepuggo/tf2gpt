import multiprocessing
import sys
from time import sleep
import os
import threading
import time

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from flask import Flask, render_template, session, request, url_for, redirect, send_from_directory
from flask_socketio import SocketIO, emit
from markupsafe import Markup

from gtts import gTTS
from dotenv import load_dotenv

import rcon
from rcon.source import Client

import replicate
from pygame import mixer
from pygame import _sdl2 as device
import vlc

from colorama import init
from colorama import Fore
from colorama import Back

from conlog import ConLog
from config import *

load_dotenv()

#socketio = SocketIO
app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading")

backstory = PROMPT

chat_memory = []
vb_support = True

# globals #
global client

last_text = ""
kill_switch = False
game_running = False
auto_disable_voice = True
queue = []

def ask(author: str, question: str):
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
    print(f"{Back.CYAN}{author}{Back.RESET}{Fore.CYAN}: {question}")
    message = replicate.run(
        "meta/llama-2-70b-chat",
        input={
            "debug": False,
            #"top_k": 50,
            "top_p": 1,
            "prompt": question,
            "temperature": 0.5,
            "system_prompt": gen_prompt,
            "max_new_tokens": 256,
            "min_new_tokens": -1
        },
    )
    full = ''.join(message)
    
    full = re.sub("^you: ?", "", full, flags=re.RegexFlag.IGNORECASE) # check if message starts with you:
    full = re.sub("^[\"\']|[\"\']$", "", full) # check if message has quotes at beginning and end
    
    chat_memory.append(f"You: {full}")
    print(Fore.GREEN + full)
    return full

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

def is_command(message, cmd):
    return message.lower().split(' ')[0] == f"{PREFIX}{cmd}"

def vb_command(message, cmd):
    return vb_support and is_command(message, cmd)

# seperate process #

player = vlc.MediaPlayer()

# Get list of output devices
def get_device(devicename):
    mods = player.audio_output_device_enum()
    if mods:
        mod = mods
        while mod:
            mod = mod.contents
            # If device is found, return its module and device id
            if devicename in str(mod.description):
                device = mod.device
                module = mod.description
                return device,module
            mod = mod.next

def _quick_play(devicename, file):
    #mixer.pre_init(devicename=devicename)
    #mixer.init()
    #mixer.music.load(file)
    #mixer.music.play()
    #while mixer.music.get_busy():
    #    pass
    #mixer.quit()
    device, module = get_device(devicename)
    media = vlc.Media(file)
    player.set_media(media)
    
    player.audio_output_device_set(None, device)
    player.play()
    while player.get_state() != 6: # ended
        pass

# end seperate process #

def play_audio(file):
    inp = multiprocessing.Process(target=_quick_play, args=[VBCABLE, file], daemon=True) 
    out = multiprocessing.Process(target=_quick_play, args=[SOUNDOUTPUT, file], daemon=True)
    
    inp.start()
    out.start()
    
    while inp.is_alive() and out.is_alive():
        if kill_switch:
            inp.kill()
            out.kill()
            break

def tts(client: Client, text):
    if text.strip() == "":
        print(f"{Fore.RED}Empty prompt in '{text}'")
        return
    global last_text
    global auto_disable_voice
    if text != last_text:
        #output = replicate.run(
        #    "lucataco/xtts-v2:684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e",
        #    input={
        #        "speaker": VOICE_TRAINING,
        #        "text": text
        #    }
        #)
        
        #response = requests.get(output, allow_redirects=True)
        #with open(CACHED_SND, "wb") as f:
        #    f.write(response.content)
        
        tts = gTTS(text=text, lang='en', tld="co.uk", slow=False)
        try:
            os.remove(CACHED_SND)
        except FileNotFoundError:
            print(Fore.RED + "file does not exist, skipping removal.")
        tts.save(CACHED_SND)
        last_text = text
    else:
        print(Fore.RED + "using cached sound")
    
    client.run('+voicerecord')
    play_audio(CACHED_SND)
    #mixer.music.load(CACHED_SND)
    #sleep(0.1)
    #mixer.music.play()
    #while mixer.music.get_busy():
    #    pass
    #mixer.quit()
    #mixer.init(devicename = VBCABLE)
    if auto_disable_voice:
        client.run('-voicerecord')

def ttsask(client: Client, username, args):
    question = " ".join(args[1:])
    tts(client, f"{username} asks: {', '.join(args[1:]) if SAY_QUESTION_LIKE_FIRST_GRADER else question}. {ask(username, question)}")
    
def ttssay(client: Client, username, args):
    text = ' '.join(args[1:])
    print(Fore.GREEN + text)
    tts(client, text)
    
def check_commands(client: Client, message: str, username: str = USERNAME):
    global chat_memory
    global backstory 
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
            print(Fore.RED + "ignored command. too few args")
            return
        backstory = ' '.join(args[1:])
        if args[1] == "default":
            backstory = PROMPT
        sleep(2)
        tts(client, f"set backstory to '{backstory if len(backstory) < BACKSTORY_MAX_LEN else f"{backstory[:BACKSTORY_MAX_LEN]} dot dot dot"}'")
        chat_memory.clear()
    elif vb_command(message, "ttsask"):
        ttsask(client, username, args)
    elif vb_command(message, "ttssay"):
        ttssay(client, username, args)

@app.route("/")
def home():
    global auto_disable_voice
    global kill_switch
    
    if not game_running:
        return render_template('err.html', error="game_not_running")
    return render_template('index.html', refreshTime=REFRESH_TIME, killSwitch=kill_switch, autoDisableVoice=auto_disable_voice)

@socketio.on("send_cmd")
def send_cmd(data: dict):
    print(data)
    message = data.get('message', '').strip()
    cmd_type = data.get('type', '').strip()
    if message == '':
        print(Fore.RED + 'message is empty')
        return
    if cmd_type not in ['ai', 'rcon']:
        print(Fore.RED + 'incorrect type')
        return
    
    if cmd_type == "ai":
        queue.append({"username": USERNAME, "message": message})
    elif cmd_type == "rcon":
        client.run(message)

@socketio.on("set_killswitch")
def set_killswitch(val: bool):
    print(f"{Fore.RED}KILLSWITCH: {val}")
    global kill_switch
    kill_switch = val
    
@socketio.on("set_auto_disable_voice")
def set_auto_disable_voice(val: bool):
    print(f"{Fore.RED}AUTO DISABLE: {val}")
    global auto_disable_voice
    auto_disable_voice = val

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
                            # add message to the end of the queue
                            if message.startswith(PREFIX):
                                queue.append({"username": username, "message": message})
                            
                    if len(queue) >= 1:
                        print(queue)
                        # get oldest message so far
                        oldest = queue[0]
                        username = oldest["username"]
                        message = oldest["message"]
                        check_commands(client, message, username)
                        del queue[0]
                        
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
    init(autoreset=True)
    mixer.pre_init(devicename = VBCABLE)
    mixer.init()

    if not VBCABLE in device.audio.get_audio_device_names(False):
        print(Fore.RED + "To use voice-related AI commands, please get Virtual Audio Cable: https://vb-audio.com/Cable/.")
        vb_support = False
    else:
        print(Fore.GREEN + "Virtual Audio Cable found. vb commands enabled!")

    mixer.quit()
    
    rcon_thread = threading.Thread(target=run_rcon_thread, daemon=True)
    rcon_try_thread = threading.Thread(target=run_rcon_try_thread, daemon=True)
    rcon_thread.start()
    rcon_try_thread.start()
    socketio.run(app, use_reloader=False)