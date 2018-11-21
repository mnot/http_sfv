
from typing import Tuple

from .util import remove_char

DQUOTE = '"'
BACKSLASH = '\\'

def parse_string(input_string: str) -> Tuple[str, str]:
    output_string = ""
    if not input_string or input_string[0] != DQUOTE:
        raise ValueError("First character of string is not DQUOTE.", input_string)
    input_string = input_string[1:]
    while input_string:
        input_string, char = remove_char(input_string)
        if char == BACKSLASH:
            if not input_string:
                raise ValueError("Last character of input was a backslash.", input_string)
            else:
                input_string, next_char = remove_char(input_string)
                if next_char not in DQUOTE + BACKSLASH:
                    raise ValueError("Backslash before disallowed character.", input_string)
                output_string += next_char
        elif char == DQUOTE:
            return input_string, output_string
        elif not 31 < ord(char) < 127:
            raise ValueError("String contains disallowed character.", input_string)
        else:
            output_string += char
    raise ValueError("Reached end of input without finding a closing DQUOTE.", input_string)

def ser_string(inval: str) -> str:
    if type(inval) is not str:
        raise ValueError("Input is not str.")
    if not all(31 < ord(char) < 127 for char in inval):
        raise ValueError("String contains disallowed characters.")
    output = ""
    output += DQUOTE
    for char in inval:
        if char in BACKSLASH + DQUOTE:
            output += BACKSLASH
        output += char
    output += DQUOTE
    return output
