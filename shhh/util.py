
from typing import Tuple

def remove_char(input_string: str) -> Tuple[str, str]:
    "Remove the first character of input_string and return it."
    if not input_string:
        raise ValueError("No next character in input.", input_string)
    next_char = input_string[0]
    input_string = input_string[1:]
    return input_string, next_char

def discard_ows(input_string: str) -> str:
    "Remove leading OWS from input_string."
    return input_string.lstrip("\t ")
