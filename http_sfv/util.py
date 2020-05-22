from typing import Tuple


def remove_char(input_string: str) -> Tuple[str, str]:
    "Remove the first character of input_string and return it."
    if not input_string:
        raise ValueError(f"No next character in input at  at: {input_string[:10]}")
    next_char = input_string[0]
    input_string = input_string[1:]
    return input_string, next_char


def discard_ows(input_string: str) -> str:
    "Remove leading space from input_string."
    return input_string.lstrip(" ")


def discard_http_ows(input_string: str) -> str:
    "remove leading space or HTAB from input_string."
    return input_string.lstrip(" \t")
