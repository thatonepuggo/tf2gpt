# builtins #
from datetime import timedelta
from enum import Enum
from http import HTTPStatus
from inspect import signature
import os
import re
from re import RegexFlag
from time import sleep

# pypi #
from flask import Response


def remove_lines(input_string, max_lines):
  """
  removes beginning lines from a string if it is greater than or equal to max_lines.
  """
  lines = input_string.split('\n')

  if len(lines) >= max_lines:
    lines = lines[-max_lines:]

  return '\n'.join(lines)


def swap(list, pos1, pos2):
  """
  swaps two items in a list
  """
  list[pos1], list[pos2] = list[pos2], list[pos1]
  return list


def chunkstring(string, length):
  """
  splits a string apart by length.
  """
  return (string[0 + i:length + i] for i in range(0, len(string), length))


def delete_line_by_char_index(input_string: str, char_index: int):
  """
  deletes a line from a string from an index.
  """
  lines = input_string.splitlines()
  line = input_string.count("\n", 0, char_index)
  if line > len(lines):
    return input_string
  if line < 0:
    return input_string
  del lines[line]
  return "\n".join(lines)


def remove_empty_lines(input_string: str):
  """
  removes empty lines from a string.
  """
  lines = input_string.split('\n')
  non_empty_lines = [line for line in lines if line.strip() != '']
  result_string = '\n'.join(non_empty_lines)
  return result_string


def is_empty(string: str):
  """
  is a string empty?
  """

  return string.strip() == ""


# for example: " version : 8622567/24 862567 secure" matches "version"
re_header_line_key = r'^[^\s]+(?= *: .*)'
re_plist_key = r'^# userid *name *uniqueid *connected *ping *loss *state'

re_plr_userid = r'(?<=# ) *[0-9]+ '
re_plr_uniqueid = r'\[U:1:[0-9]+\]'
re_plr_state = r'(active|spawning)'
re_plr_loss = r'[0-9]+$'

re_multiple_spaces = r' +'


def filter_status(status: str):
  """
  filters through the output of a `status` command.
  """
  ret = status

  def _remove_header_line(key):
    for i in re.finditer(re_header_line_key, ret, RegexFlag.MULTILINE):
      if i.group() == key:
        return delete_line_by_char_index(ret, i.start())
    return ret

  ret = _remove_header_line("version")
  ret = _remove_header_line("udp/ip")
  ret = _remove_header_line("steamid")
  ret = _remove_header_line("account")
  ret = _remove_header_line("tags")
  ret = _remove_header_line("edicts")

  # remove # userid uniqueid ...
  ret = re.sub(re_plist_key, "", ret, flags=RegexFlag.MULTILINE)

  # remove unimportant data in users
  # two re_plr_loss's are used to remove loss and ping
  regexes_to_run = [re_plr_userid, re_plr_uniqueid,
                    re_plr_state, re_plr_loss, re_plr_loss, re_multiple_spaces]
  retsplit = ret.splitlines()
  for index, line in enumerate(retsplit):
    if line.startswith("#"):
      for regex in regexes_to_run:
        retsplit[index] = re.sub(
            regex, " ", retsplit[index], flags=RegexFlag.MULTILINE)

  ret = "\n".join(retsplit)

  ret = remove_empty_lines(ret)
  print(ret)
  return ret


def substitute_words(text: str, words: dict):
  """
  substitutes words in the text with substitutions.
  used to help gtts pronounce some special characters.
  """
  for word, replacement in words.items():
    replace_pattern = re.compile(r'(?<!\S)%s(?!\S)' % re.escape(word))
    text = replace_pattern.sub(re.escape(replacement), text)
  return text


def duration(string: str) -> timedelta:
  """
  parses a duration string (like 10d 24h 10m 5s 2ms) into a timedelta (like timedelta(milliseconds=951005002))
  see function definition for list of units.
  """
  # from https://stackoverflow.com/a/54905404
  UNITS = {
      "ms": 1,
      "s": 1000,
      "m": 1000 * 60,
      "h": 1000 * 60 * 60,
      "d": 1000 * 60 * 60 * 24,
  }
  regex = r"(\d+(?:\.\d)?)(" + \
      "|".join([re.escape(key) for key in UNITS.keys()]) + r")"
  parts = re.findall(regex, string)
  final = sum(float(x) * UNITS[m] for x, m in parts)
  return timedelta(milliseconds=final)


def sleep_duration(string: str):
  """
  sleeps using a duration string (see util.duration.)
  """
  sleep(duration(string).total_seconds())


def quick_json_response(json: dict | list, status: HTTPStatus = HTTPStatus.OK) -> Response:
  """
  creates a Response object and adds json to it
  """
  return Response(
      json,
      status=status,
      mimetype="application/json"
  )


def quick_exit_code(code: str = "success", status: HTTPStatus | None = None) -> Response:
  """
  creates a Response object and adds an exit code json to it
  """
  return quick_json_response({"code": code}, status)


class PAModArgs_State(Enum):
  WHITESPACE = 0
  KEY = 1
  VALUE_START = 2
  VALUE_SIMPLE = 3
  VALUE_DOUBLE_QUOTES = 4
  VALUE_TICKS = 5


def parse_pa_modargs(args: str) -> dict:
  """
  parses pulseaudio's string modargs into a dictionary.
  """
  ret = {}

  if args is None:
    return ret

  args += " "

  if args:
    ind = 0

    key = 0
    value = 0

    key_len = 0
    value_len = 0

    def _add(_value=None):
      if _value is None:
        _value = args[value:value_len + value]
      ret[args[key:key_len + key]] = _value

    state = PAModArgs_State.WHITESPACE

    while ind < len(args):
      char = args[ind]
      match state:
        case PAModArgs_State.WHITESPACE:
          if char == "=":
            return ret
          elif not char.isspace():
            key = ind
            key_len = 1
            state = PAModArgs_State.KEY
        case PAModArgs_State.KEY:
          if char == "=":
            state = PAModArgs_State.VALUE_START
          else:
            key_len += 1
        case PAModArgs_State.VALUE_START:
          if char == "'":
            state = PAModArgs_State.VALUE_TICKS
            value = ind + 1
            value_len = 0
          elif char == "\"":
            state = PAModArgs_State.VALUE_DOUBLE_QUOTES
            value = ind + 1
            value_len = 0
          elif char.isspace():
            ret[args[key:key + key_len]] = ""
            state = PAModArgs_State.WHITESPACE
          else:
            state = PAModArgs_State.VALUE_SIMPLE
            value = ind
            value_len = 1
        case PAModArgs_State.VALUE_SIMPLE:
          if char.isspace():
            _add()
            state = PAModArgs_State.WHITESPACE
          else:
            value_len += 1
        case PAModArgs_State.VALUE_DOUBLE_QUOTES:
          if char == "\"":
            _add()
            state = PAModArgs_State.WHITESPACE
          else:
            value_len += 1
        case PAModArgs_State.VALUE_TICKS:
          if char == "'":
            _add()
            state = PAModArgs_State.WHITESPACE
          else:
            value_len += 1
      ind += 1
  return ret


def ignore_simple(function):
  count = len(signature(function).parameters)
  return lambda *args: function(*args[:count])


llama_escapes = {
    "\\": "\\\\",
    "[": "\\[",
    "]": "\\]",
    "<<": "\\<<",
    ">>": "\\>>"
}


def escape_llama_prompt(inp: str) -> str:
  for old, new in llama_escapes.items():
    inp = inp.replace(old, new)
  return inp


def unescape_llama_prompt(inp: str) -> str:
  for old, new in llama_escapes.items()[::-1]:
    inp = inp.replace(new, old)
  return inp
