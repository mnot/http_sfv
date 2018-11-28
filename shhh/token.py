
from string import ascii_letters, digits
from typing import Tuple

from .util import remove_char

def parse_token(input_string: str) -> Tuple[str, str]:
    if not input_string or input_string[0] not in ascii_letters:
        raise ValueError("Token didn't start with ALPHA.", input_string)
    output_string = ""
    while input_string:
        input_string, char = remove_char(input_string)
        if not char in ascii_letters + digits + "_-.:%*/":
            input_string = char + input_string
            return input_string, output_string
        output_string += char
    return input_string, output_string

def ser_token(token: str) -> str:
    if type(token) is not str:
        raise ValueError("Token is not str.")
    if not all(char in ascii_letters + digits + "_-.:%*/" for char in token):
        raise ValueError("Token contains disallowed characters.")
    output = ""
    output += token
    return output
