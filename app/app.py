import multiprocessing
import re
import sys
from time import sleep
import os
import threading
import time

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from flask import Flask, render_template, session, request, url_for, redirect, send_from_directory
from flask_socketio import SocketIO, emit

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
from config import config
from aicmd import AICommand
from soundplayer import SoundPlayer
import util
import blocked_words

import textwrap

from IPython.display import display
from IPython.display import Markdown
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
socketio = SocketIO(app, async_mode="threading")

backstory = config.data["prompt"]

chat_memory = []
vb_support = True

# constants #
re_username = re.compile(r'.*(?= :)')
re_message = re.compile(r'(?<=. : ).*')

CONNECT_EXCEPTIONS = (ConnectionRefusedError, ConnectionResetError, rcon.SessionTimeout, rcon.WrongPassword, rcon.EmptyResponse)

SELF_ADDRESS = '127.0.0.1'
SELF_PORT = 27015
# globals #
global client

last_text = ""
game_running = False
queue = []
conlog = ConLog(game_root=config.data["gameroot"], mod_root=config.data["modroot"])
sp = SoundPlayer()

def ask(author: str, question: str):
    global backstory
    global chat_memory
    global client
    chat_memory = chat_memory[-20:]
    memory_string = '\n'.join(chat_memory)
    #status_string = util.filter_status(conlog.get_status(client))

    """
here is your conversation info. it includes the name of the server, and who is in it. it also includes the time they've been here.
---beginning of conversation info, use this as reference---
{status_string}
---end of conversation info---
    """

    gen_prompt = f"""{backstory}
here is your current chat history, use this to remember context from earlier. (if 'You' said this, you said this. Otherwise, that was a user.).
this is for you to refrence as memory, not to use in chat. i.e. "oh yes, i remember you saying this some time ago." if it isn't acutally in history, dont say it.
---beginning of your chat history, use this as memory.---
{memory_string}
---end of your chat history---
---beginning of current chat message---
[INST] {author}: {question} [/INST]
<your message here>"""
    #print(gen_prompt)

    chat_memory.append(f"{author}: {question}")
    
    # print question
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
    full = "".join(message)
    
    # cleanup string #
    full = re.sub("^( )?you: ?", "", full, flags=re.RegexFlag.IGNORECASE) # check if message starts with you:
    full = re.sub("^[\"\']|[\"\']$", "", full) # check if message has quotes at beginning and end
    full = full.strip()
    
    chat_memory.append(f"You: {full}")
    return full

def tts(client: Client, text, print_text = True):
    if text.strip() == "":
        print(f"{Fore.RED}Empty prompt in '{text}'")
        return
    global last_text
    if text != last_text:
        # translate the text
        translated_text = util.translate_text(text, config.data["tts_translations"].get("words", {}))

        try:
            tts = gTTS(text=translated_text, lang='en', tld=config.data["gtts_tld"], slow=False)
            try:
                os.remove(config.data["cached_snd"])
            except (FileNotFoundError, PermissionError):
                print(Fore.RED + "some errro, skipping removal.")
            tts.save(config.data["cached_snd"])
            last_text = text
        except AssertionError as e:
            print(f"{Fore.RED}gTTS shit itself: {e}")
    else:
        print(Fore.RED + "using cached sound")
    
    if print_text:
        print(Fore.GREEN + text + "\n")
    sp.play(client, config.data["cached_snd"])

def cmd_backstory(client: Client, username: str, message: str, args: list[str]):
    global backstory
    if len(args) == 0:
        return
    backstory = ' '.join(args[1:])
    if args[1] == "default":
        backstory = config.data["prompt"]
    sleep(2)

    # trim the backstory (so the ai doesn't say the entire thing if it's incredibly long)
    trimmed_backstory = backstory if len(backstory) < config.data["backstory_max_len"] else f"{backstory[:config.data["backstory_max_len"]]} dot dot dot"
    
    print(f"{Fore.CYAN}set backstory: {backstory}")
    
    tts(client, f"set backstory to '{trimmed_backstory} ", print_text = False)
    
    chat_memory.clear()

def cmd_ttsask(client: Client, username: str, message: str, args: list[str]):
    sp.play(client, config.data["processing_snd"])
    question = " ".join(args[1:])
    question_to_say = ', '.join(args[1:]) if config.data["say_question_like_first_grader"] else question

    filtered = blocked_words.blocked_words_filter(question)
    if filtered == "":
        return
    
    tts(client, f"{username} asks: {question_to_say}: {ask(username, filtered)}")

def cmd_ttssay(client: Client, username: str, message: str, args: list[str]):
    text = ' '.join(args[1:])
    
    filtered = blocked_words.blocked_words_filter(text)
    if filtered == "":
        return
    
    tts(client, filtered)

def cmd_queuelength(client: Client, username: str, message: str, args: list[str]):
    tts(client, f"the queue is currently {len(queue)} message{'s' if len(queue) != 1 else ''} long")

commands = [
    AICommand(name="backstory", aliases=["become", "bs", "prompt"], func=cmd_backstory, min_args=1),
    AICommand(name="ttsask", aliases=["ask", "ttask"], func=cmd_ttsask, min_args=1, voice=True),
    AICommand(name="ttssay", aliases=["say", "ttsay"], func=cmd_ttssay, min_args=1, voice=True),
    AICommand(name="queuelength", aliases=["queuelen", "length", "len"], func=cmd_queuelength, min_args=0, voice=True),
]

def check_commands(client: Client, username: str = config.data["username"], message: str = "", run = True):
    global sp
    if sp.kill_switch:
        return
    args = message.split(' ')
    for cmd in commands:
        name = cmd.name
        can_run = cmd.is_command(message)
        if cmd.voice and not vb_support:
            can_run = False
        if can_run:
            if run: # only run the command if run is enabled
                cmd.exec(client, username, message)
            return name # otherwise return name
    return False

@app.route("/")
def home():
    global sp
    
    if not game_running:
        return render_template('err.html', error="game_not_running")
    return render_template('index.html', refreshTime=config.data["refresh_time"], killSwitch=sp.kill_switch, autoDisableVoice=sp.auto_disable_voice)

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
        queue.insert(0, {"username": config.data["username"], "message": config.data["prefix"] + message})
    elif cmd_type == "rcon":
        client.run(message)
        
@socketio.on("queue_action")
def queue_action(data: dict):
    global queue
    index = data["index"]
    action = data["action"]
    print(index, action)
    if len(queue) < index + 1:
        return False
    item = queue[index]
    if action == 0: # delete
        del queue[index]
    elif action == 1: # send up
        if index - 1 < 0:
            return False
        queue = util.swap(queue, index, index - 1)
    elif action == 2: # send down
        if index + 1 >= len(queue):
            return False
        queue = util.swap(queue, index, index + 1)
    elif action == 3: # send to front
        del queue[index]
        queue.insert(0, item)
    elif action == 4: # send to back
        del queue[index]
        queue.insert(len(queue) + 1, item)
    send_queue()
    
@socketio.on("set_killswitch")
def set_killswitch(val: bool):
    print(f"{Fore.RED}KILLSWITCH: {val}")
    global sp
    sp.kill_switch = val
    
@socketio.on("set_auto_disable_voice")
def set_auto_disable_voice(val: bool):
    print(f"{Fore.RED}AUTO DISABLE: {val}")
    global sp
    sp.auto_disable_voice = val


def run_rcon_thread():
    global game_running
    global client
    global queue
    global conlog
    global sp
    while True:
        try:
            with Client(SELF_ADDRESS, SELF_PORT, passwd=config.data["password"]) as client:
                while True:
                    if sp.kill_switch:
                        continue
                    
                    if len(queue) >= 1:
                        # get oldest message so far
                        oldest = queue.pop(0)
                        username = oldest["username"]
                        message = oldest["message"]
                        check_commands(client, username, message) # run command
                        
                    sleep(config.data["refresh_time"])
        except CONNECT_EXCEPTIONS:
            pass

def send_queue():
    escaped_queue = []
    for i in queue:
        queue_thing = {"username": util.escape_markup(i["username"]), "message": util.escape_markup(i["message"])}
        escaped_queue.append(queue_thing)
    socketio.emit("queueget", escaped_queue)

was_connected = False
def run_rcon_try_thread():
    global game_running
    global was_connected
    while True:
        try:
            with Client(SELF_ADDRESS, SELF_PORT, passwd=config.data["password"]) as try_client:
                if not was_connected:
                    print(Fore.GREEN + "Connected!")
                game_running = True
                was_connected = True
        except CONNECT_EXCEPTIONS as e:
            print(Fore.RED + "Could not connect to game: " + str(e))
            print(Fore.RED + """
Please check if you: 
    - have `-condebug -conclearlog -usercon -g15` in your launch options
    - have the correct lines in your autoexec
""")
            game_running = False
            was_connected = False
        sleep(config.data["connection_check_time"])
        
def run_rcon_ping_thread():
    global conlog
    while True:
        try:
            with Client(SELF_ADDRESS, SELF_PORT, passwd=config.data["password"]) as ping_client:
                while True:
                    # update the queue
                    new = conlog.readnewlines()

                    for line in new:
                        username_match = re_username.search(line)
                        message_match = re_message.search(line)

                        if username_match and message_match:
                            username = username_match.group()
                            message = message_match.group().lstrip()
                            # add message to the end of the queue
                            if check_commands(client, username, message, False):
                                queue.append({"username": username, "message": message})
                                
                    # send the log
                    escaped_log = util.remove_lines(conlog.read(), config.data["log_max_lines"])
                    escaped_log = util.escape_markup(escaped_log)
                    socketio.emit("consoleget", escaped_log)

                    # send the queue
                    send_queue()
                    sleep(config.data["refresh_time"])
                    
        except CONNECT_EXCEPTIONS:
            pass

if __name__ == '__main__':
    init(autoreset=True)
    mixer.pre_init(devicename = config.data["vbcable"])
    mixer.init()

    if not config.data["vbcable"] in device.audio.get_audio_device_names(False):
        print(Fore.RED + "To use voice-related AI commands, please get Virtual Audio Cable: https://vb-audio.com/Cable/.")
        vb_support = False
    else:
        print(Fore.GREEN + "Virtual Audio Cable found. vb commands enabled!")

    mixer.quit()
    
    rcon_thread = threading.Thread(target=run_rcon_thread, daemon=True)
    rcon_try_thread = threading.Thread(target=run_rcon_try_thread, daemon=True)
    rcon_ping_thread = threading.Thread(target=run_rcon_ping_thread, daemon=True)
    rcon_thread.start()
    rcon_try_thread.start()
    rcon_ping_thread.start()
    socketio.run(app, use_reloader=False)