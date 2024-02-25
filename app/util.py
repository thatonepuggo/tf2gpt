from markupsafe import Markup

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