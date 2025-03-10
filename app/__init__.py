# stdlib #
from http import HTTPStatus
import sys
from subprocess import Popen
import threading

# pypi #
from flask import Blueprint, Flask, render_template, request
from flask_socketio import SocketIO, emit

from dotenv import load_dotenv

from rcon.source import Client
from sty import fg, bg, ef, rs


# local #
from .config import config
from .consts import CONNECT_EXCEPTIONS, SUPPORTED_PLATFORMS, RE_USERNAME, RE_MESSAGE, SOURCE_ADDRESS, SOURCE_PORT
from .aicmd import AICommand
from .soundplayer import SoundPlayer
from .queuemanager import QueueItem, json_queue, queue
from .ttsmanager import tts
from .watchers import CallbackWatcher
from . import state
from . import soundplayer
from . import util
from . import blocked_words
from . import aimanager

load_dotenv()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
socketio = SocketIO(app, async_mode="threading")


# TODO: maybe asyncio?

# commands #


def cmd_backstory(username: str, message: str, args: list[str]):
  if len(args) == 0:
    return
  backstory = ' '.join(args[1:])
  if args[1] == "default":
    backstory = config.data["backstory"]

  # trim the backstory (so the ai doesn't say the entire thing if it's incredibly long)
  trimmed_backstory = (
      backstory
      if len(backstory) < config.data["backstory_max_tts_len"]
      else f"{backstory[:config.data["backstory_max_tts_len"]]} dot dot dot"
  )

  print(f"{fg.cyan}set backstory: {backstory}{rs.all}")

  tts(f"set backstory to {trimmed_backstory}")

  aimanager.chat_memory.clear()


def cmd_ttsask(username: str, message: str, args: list[str]):
  soundplayer.sp.play(config.data["processing_snd"])
  question = " ".join(args[1:])
  question_to_say = ', '.join(
      args[1:]) if config.data["say_question_like_first_grader"] else question

  filtered = blocked_words.blocked_words_filter(question)

  tts(f"{username} asks: {question_to_say}: {aimanager.ask(username, filtered)}", print_text=True)


def cmd_ttssay(username: str, message: str, args: list[str]):
  text = ' '.join(args[1:])

  filtered = blocked_words.blocked_words_filter(text)

  tts(filtered, print_text=True)


def cmd_queuelength(username: str, message: str, args: list[str]):
  tts(f"the queue is currently {len(queue)} request{'s' if len(queue) != 1 else ''} long")


# TODO: use a decorator instead of a list
commands = [
    AICommand(
        name="backstory",
        aliases=["become", "bs", "prompt"],
        func=cmd_backstory,
        min_args=1
    ),
    AICommand(
        name="ttsask",
        aliases=["ask", "ttask"],
        func=cmd_ttsask,
        min_args=1,
        voice=True
    ),
    AICommand(
        name="ttssay",
        aliases=["say", "ttsay"],
        func=cmd_ttssay,
        min_args=1,
        voice=True
    ),
    AICommand(
        name="queuelength",
        aliases=["queuelen", "length", "len"],
        func=cmd_queuelength,
        min_args=0,
        voice=True
    ),
]


def check_commands(username: str = config.data["username"], message: str = "", run=True):
  if soundplayer.sp.kill_switch:
    return
  args = message.split(' ')
  for cmd in commands:
    name = cmd.name

    if cmd.matches(message):
      if run:  # only run the command if run is enabled
        cmd.exec(username=username, message=message)
      return name  # otherwise return name

  return False


def json_queue():
  return [vars(item) for item in queue]

# routes #


@app.route("/")
def home():
  if not state.is_connected:
    return render_template('err.html', error="game_not_running")
  return render_template('index.html')


@app.route("/cmd", methods=["POST"])
def send_cmd():
  data = request.json

  message = data.get('message', '').strip()
  cmd_type = data.get('type', '').strip()
  if message == '':
    print(f'{fg.red}message is empty{rs.all}')
    return util.quick_exit_code("messsage_empty", HTTPStatus.BAD_REQUEST)

  match cmd_type:
    case "ai":
      queue.appendleft(QueueItem(
          username=config.data["username"],
          message=config.data["prefix"] + message,
          is_system=True
      ))
      socketio.emit("broadcast_queue", json_queue())
    case _:
      print(f"{fg.red}invalid command type '{cmd_type}'{rs.all}")
      return util.quick_exit_code("invalid_command_type", HTTPStatus.BAD_REQUEST)

  return util.quick_exit_code()


def process_console() -> str:
  return util.remove_lines(
      state.conlog.read(), config.data["log_max_lines"])


# panel vars #

def json_pvars() -> dict:
  return {
      "kill_switch": soundplayer.sp.kill_switch,
      "auto_disable_voice": soundplayer.sp.auto_disable_voice,
  }


connected_users = set()


def update_connected_users():
  print(connected_users)
  emit("connected_count", len(connected_users), broadcast=True)


@socketio.event
def connect():
  emit("broadcast_queue", json_queue())
  emit("broadcast_pvars", json_pvars())
  emit("broadcast_console", process_console())
  connected_users.add(request.sid)
  update_connected_users()


@socketio.event
def disconnect():
  connected_users.remove(request.sid)
  update_connected_users()


@socketio.event
def queue_action(data: dict):
  global queue
  index = data["index"]
  action = data["action"]
  print(f"queue_action: {action} on #{index}")

  if index < 0 or index >= len(queue):
    print(f"out of range {index} (len = {len(queue)})")
    return

  item = queue[index]
  match action:
    case "delete":
      del queue[index]
    case "swap_up":
      # swaps with above
      if index - 1 < 0:
        return
      queue[index], queue[index - 1] = queue[index - 1], queue[index]
    case "swap_down":
      # swap with below
      if index + 1 >= len(queue):
        return
      queue[index], queue[index + 1] = queue[index + 1], queue[index]
    case "front":
      # send to front
      del queue[index]
      queue.appendleft(item)
    case "back":
      # send to back
      del queue[index]
      queue.append(item)
    case _:
      print(f"{fg.red}unknown action '{action}'.{rs.all}")

  emit("broadcast_queue", json_queue(), broadcast=True)


@socketio.event
def set_pvars(data: dict):
  soundplayer.sp.kill_switch = data.get("kill_switch", soundplayer.sp.kill_switch)
  soundplayer.sp.auto_disable_voice = data.get("auto_disable_voice", soundplayer.sp.auto_disable_voice)

  emit("broadcast_pvars", json_pvars(), broadcast=True, include_self=False)


def update_console():
  # update the queue
  new = state.conlog.readnewlines()

  for line in new:
    username_match = RE_USERNAME.search(line)
    message_match = RE_MESSAGE.search(line)

    if username_match and message_match:
      username = username_match.group()
      message = message_match.group().lstrip()
      # add message to the end of the queue
      if check_commands(username=username, message=message, run=False):
        queue.append(QueueItem(username=username, message=message))
        # send the queue
        socketio.emit("broadcast_queue", json_queue())

  # send the console
  socketio.emit("broadcast_console", process_console())

# threads #


def run_rcon():
  # this is extremely messy, i should really try async
  while True:
    try:
      with Client(SOURCE_ADDRESS, SOURCE_PORT, passwd=config.data["password"], timeout=5) as _client:
        if not state.previously_connected or state.first_connection:
          print(f"{fg.green}Connected!{rs.all}")
        state.client = _client
        state.is_connected = True
        state.previously_connected = True
        state.first_connection = False

        while True:
          pass
    except CONNECT_EXCEPTIONS as e:
      if state.previously_connected or state.first_connection:
        print(f"""{fg.red}Could not connect to game. Error: {e}
Please check if you:
    - have `-condebug -conclearlog -usercon -g15` in your launch options
    - have the correct lines in your autoexec
If none of the above work, please file an issue:
    {fg.blue}https://github.com/thatonepuggo/tf2gpt/issues{rs.all}""")
      state.is_connected = False
      state.previously_connected = False
      state.first_connection = False


def run_console_watcher():
  watcher = CallbackWatcher(state.conlog.logfile, update_console)
  watcher.run()


def run_queue_cycler():
  while True:
    if soundplayer.sp.kill_switch:
      continue

    if len(queue) >= 1:
      # get leftmost of queue (oldest messages)
      oldest = queue.popleft()
      username = oldest.username
      message = oldest.message
      socketio.emit("broadcast_queue", json_queue())
      check_commands(username, message)  # run command


def run_panel():
  build_dir_blueprint = Blueprint('build', __name__, static_url_path='/build', static_folder='_build')
  app.register_blueprint(build_dir_blueprint)

  Popen(["deno", "task", "watch"])
  socketio.run(app, use_reloader=False, host="0.0.0.0")

# main #


def run():
  if sys.platform not in SUPPORTED_PLATFORMS:
    raise NotImplementedError(f"platform {sys.platform} is not supported.")

  if config.version < 2:
    print(
        f"""{bg.yellow}{fg.black}ALERT{rs.all}
{fg.yellow}recently, tf2gpt's development was revived. with it came some breaking changes to the config file.
we have detected your config might be incompatible with the new version. please create a new config.{rs.all}"""
    )
    sys.exit(1)

  with SoundPlayer() as _sp:
    soundplayer.sp = _sp

    threads = [
        threading.Thread(target=run_rcon, daemon=True),
        threading.Thread(target=run_console_watcher, daemon=True),
        threading.Thread(target=run_queue_cycler, daemon=True),
        threading.Thread(target=run_panel, daemon=True),
    ]
    for t in threads:
      t.start()
    for t in threads:
      t.join()
