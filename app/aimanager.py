# stdlib #
import re

# pypi #
import replicate
from sty import fg, bg, ef, rs


# local #
from .util import escape_llama_prompt, filter_status, unescape_llama_prompt
from . import state
from . import config


class AIMessage:
  sent_by_ai: bool
  author: str | None
  message: str

  def __init__(self, author: str | None = None, message: str = "", sent_by_ai: bool = False):
    self.author = author
    self.message = message
    self.sent_by_ai = sent_by_ai

  def __str__(self):
    ret = f"{f"{escape_llama_prompt(self.author)}: " if self.author else ""}{escape_llama_prompt(self.message)}"
    if not self.sent_by_ai:
      ret = f"[INST]{ret}[/INST]"
    return ret


chat_memory: list[AIMessage] = []
backstory: str = config.data["backstory"]


def ask(author: str, question: str):
  global backstory
  global chat_memory
  # chat_memory = chat_memory[-20:]
  memory_string = '\n'.join([str(msg) for msg in chat_memory])
  status_string = filter_status(state.conlog.get_status())

  """
here is your conversation info. it includes the name of the server, and who is in it. it also includes the time they've been here.
---beginning of conversation info, use this as reference---
{status_string}
---end of conversation info---
    """

  user_message = AIMessage(author, question)

  gen_prompt = f"""
<<SYS>>
{backstory}
---
here is your conversation info. it includes the name of the server, and who is in it. it also includes the time they've been here:

{escape_llama_prompt(status_string)}

you do not always have to use this in your response, although you can mention it if relevant.
<</SYS>>
{memory_string}
{user_message}"""
  # print(gen_prompt)

  chat_memory.append(user_message)
  # print question
  print(f"{bg.cyan}{author}{bg.rs}{fg.cyan}: {question}{rs.all}")

  message = replicate.run(
      "meta/llama-2-70b-chat",
      input={
          "debug": False,
          # "top_k": 50,
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
  # check if message starts with you:
  full = re.sub(r"^(\s)?you: ?", "", full, flags=re.RegexFlag.IGNORECASE)
  full = full.strip()
  # check if message has quotes at beginning and end
  full = re.sub(r"^[\"\']|[\"\']$", "", full)
  full = full.strip()

  chat_memory.append(AIMessage(message=full, sent_by_ai=True))

  return full
