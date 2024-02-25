from markupsafe import Markup
import re
from re import RegexFlag

def escape_markup(string: str) -> str:
    """
    escape a string for html
    """
    return str(Markup.escape(string)).replace("\n", "<br>")

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
    return (string[0+i:length+i] for i in range(0, len(string), length))

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
    regexes_to_run = [re_plr_userid, re_plr_uniqueid, re_plr_state, re_plr_loss, re_plr_loss, re_multiple_spaces]
    retsplit = ret.splitlines()
    for index, line in enumerate(retsplit):
        if line.startswith("#"):
            for regex in regexes_to_run:
                retsplit[index] = re.sub(regex, " ", retsplit[index], flags=RegexFlag.MULTILINE)
                retsplit[index] = retsplit[index].strip()
    
    ret = "\n".join(retsplit)
    
    ret = remove_empty_lines(ret)
    print(ret)
    return ret