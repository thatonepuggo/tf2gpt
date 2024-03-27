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

#import replicate
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

import textwrap
import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown
from dotenv import load_dotenv

load_dotenv()

# Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.
GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')

genai.configure(api_key=GOOGLE_API_KEY)

safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

model = genai.GenerativeModel('gemini-pro', safety_settings)

#socketio = SocketIO
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

# globals #
global client

last_text = ""
kill_switch = False
game_running = False
auto_disable_voice = True
queue = []
conlog = ConLog(game_root=config.data["gameroot"], mod_root=config.data["modroot"])
sp = SoundPlayer()

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def ask(author: str, question: str):
    global backstory
    global chat_memory
    global client
    chat_memory = chat_memory[-20:]
    memory_string = '\n'.join(chat_memory)
    #client.run("__begin_status_output__")
    #client.run("status")
    #sleep(1)
    #client.run("__end_staftus_output__")
    #recording = False
    #status = ""
    #sleep(2)
    #newlines = conlog.readnewlines()
    #for line in newlines:
    #    print(line)
    #    if "Unknown command: __begin_status_output__" in line:
    #        recording = True
    #    elif "Unknown command: __end_status_output__" in line:
    #        recording = False
    #    if recording:
    #        status += line + "\n"
    
    #status = conlog.status(client)
    #print(status)
    
    #return "hold up"
    
    """
    here is your conversation info. it includes the name of the server, and who is in it. it also includes the time they've been here.
    ---beginning of conversation info, use this as reference---
    {util.filter_status(status)}
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
You: <your message here>"""
    #print(gen_prompt)

    chat_memory.append(f"{author}: {question}")
    
    # print question
    print(f"{Back.CYAN}{author}{Back.RESET}{Fore.CYAN}: {question}")
    
    """
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
    """

    response = model.generate_content("talk in first person unless the following backstory says not to: " + "\n" + backstory + "\n" + question)

    full = response.text
    
    full = re.sub("^you: ?", "", full, flags=re.RegexFlag.IGNORECASE) # check if message starts with you:
    full = re.sub("^[\"\']|[\"\']$", "", full) # check if message has quotes at beginning and end
    
    chat_memory.append(f"You: {full}")
    print(Fore.GREEN + full + "\n")
    return full

def tts(client: Client, text):
    if text.strip() == "":
        print(f"{Fore.RED}Empty prompt in '{text}'")
        return
    global last_text
    if text != last_text:
        #output = replicate.run(
        #    "lucataco/xtts-v2:684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e",
        #    input={
        #        "speaker": config.data["voice_training"],
        #        "text": text
        #    }
        #)
        
        #response = requests.get(output, allow_redirects=True)
        #with open(config.data["cached_snd"], "wb") as f:
        #    f.write(response.content)
        
        # translate the text
        translated_text = text
        words = config.data["tts_translations"].get("words", {})
        for word, replacement in words.items():
            pattern = re.compile(r'(^|\s){}(\s|$)'.format(re.escape(word)))
            translated_text = pattern.sub(r'\1{}\2'.format(replacement), translated_text)
        
        tts = gTTS(text=translated_text, lang='en', tld="co.uk", slow=False)
        #engine = pyttsx3.init()
        #engine.save_to_file(text, config.data["cached_snd"])
        #engine.runAndWait()
        try:
            os.remove(config.data["cached_snd"])
        except FileNotFoundError:
            print(Fore.RED + "file does not exist, skipping removal.")
        tts.save(config.data["cached_snd"])
        last_text = text
    else:
        print(Fore.RED + "using cached sound")
    
    sp.play(client, config.data["cached_snd"])
    #mixer.music.load(config.data["cached_snd"])
    #sleep(0.1)
    #mixer.music.play()
    #while mixer.music.get_busy():
    #    pass
    #mixer.quit()
    #mixer.init(devicename = config.data["vbcable"])

def cmd_backstory(client: Client, username: str, message: str, args: list[str]):
    global backstory
    backstory = ' '.join(args[1:])
    if args[1] == "default":
        backstory = config.data["prompt"]
    sleep(2)
    trimmed_backstory = backstory if len(backstory) < config.data["backstory_max_len"] else f"{backstory[:config.data["backstory_max_len"]]} dot dot dot"
    print(f"{Fore.CYAN}set backstory: {backstory}")
    tts(client, f"set backstory to '{trimmed_backstory} ")
    chat_memory.clear()

def cmd_ttsask(client: Client, username: str, message: str, args: list[str]):
    sp.play(client, config.data["processing_snd"])
    question = " ".join(args[1:])
    tts(client, f"{username} asks: {', '.join(args[1:]) if config.data["say_question_like_first_grader"] else question}: {ask(username, question)}")

def cmd_ttssay(client: Client, username: str, message: str, args: list[str]):
    text = ' '.join(args[1:])
    print(Fore.GREEN + text + "\n")
    tts(client, text)

commands = [
    AICommand(name="backstory", aliases=["become", "story", "bs", "prompt"], func=cmd_backstory, min_args=1),
    AICommand(name="ttsask", aliases=["ask", "task", "ttask"], func=cmd_ttsask, min_args=1, voice=True),
    AICommand(name="ttssay", aliases=["say", "tsay", "ttsay"], func=cmd_ttssay, min_args=1, voice=True),
]

def check_commands(client: Client, username: str = config.data["username"], message: str = "", run = True):
    if kill_switch:
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
    global auto_disable_voice
    global kill_switch
    
    if not game_running:
        return render_template('err.html', error="game_not_running")
    return render_template('index.html', refreshTime=config.data["refresh_time"], killSwitch=kill_switch, autoDisableVoice=auto_disable_voice)

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
        queue.insert(0, {"username": config.data["username"], "message": message})
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
    elif action == 3: # send to top
        del queue[index]
        queue.insert(0, item)
    elif action == 4: # send to back
        del queue[index]
        queue.insert(len(queue) + 1, item)
    send_queue()
    
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
    global queue
    global conlog
    while True:
        try:
            with Client('127.0.0.1', 27015, passwd=config.data["password"]) as client:
                while True:
                    if kill_switch:
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
    
def run_rcon_try_thread():
    global game_running
    while True:
        try:
            with Client('127.0.0.1', 27015, passwd=config.data["password"]) as try_client:
                game_running = True
        except CONNECT_EXCEPTIONS:
            game_running = False
        sleep(config.data["connection_check_time"])
        
def run_rcon_ping_thread():
    global conlog
    while True:
        try:
            with Client('127.0.0.1', 27015, passwd=config.data["password"]) as ping_client:
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