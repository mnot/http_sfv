from string import ascii_letters, digits
from typing import Tuple

from .util import remove_char

TOKEN_CHARS = ascii_letters + digits + ":/!#$%&'*+-.^_`|~"


class Token(str):
    pass


def parse_token(input_string: str) -> Tuple[str, str]:
    if not input_string or input_string[0] not in ascii_letters:
        raise ValueError("Token didn't start with ALPHA.", input_string)
    output_string = ""
    while input_string:
        input_string, char = remove_char(input_string)
        if not char in TOKEN_CHARS:
            input_string = char + input_string
            return input_string, output_string
        output_string += char
    return input_string, Token(output_string)


def ser_token(token: str) -> str:
    if not all(char in TOKEN_CHARS for char in token):
        raise ValueError("Token contains disallowed characters.")
    output = ""
    output += token
    return output
