
from string import ascii_lowercase, digits
from typing import Tuple

from .util import remove_char

def parse_identifier(input_string: str) -> Tuple[str, str]:
    if not input_string or input_string[0] not in ascii_lowercase:
        raise ValueError("Identifier didn't start with lcalpha.", input_string)
    output_string = ""
    while input_string:
        input_string, char = remove_char(input_string)
        if not char in ascii_lowercase + digits + "_-.:%*/":
            input_string = char + input_string
            return input_string, output_string
        output_string += char
    return input_string, output_string

def ser_identifier(identifier: str) -> str:
    if type(identifier) is not str:
        raise ValueError("Identifier is not str.")
    if not all(char in ascii_lowercase + digits + "_-.:%*/" for char in identifier):
        raise ValueError("Identifier contains disallowed characters.")
    output = ""
    output += identifier
    return output
