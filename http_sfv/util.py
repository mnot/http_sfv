from string import ascii_lowercase, digits
from typing import List, Tuple


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


KEY_START_CHARS = set(ascii_lowercase + "*")
KEY_CHARS = set(ascii_lowercase + digits + "_-*.")


def parse_key(input_string: str) -> Tuple[str, str]:
    if input_string and input_string[0] not in KEY_START_CHARS:
        raise ValueError(
            f"Key does not begin with lcalpha or * at: {input_string[:10]}"
        )
    output_string: List[str] = []
    while input_string:
        if input_string[0] not in KEY_CHARS:
            return input_string, "".join(output_string)
        input_string, char = remove_char(input_string)
        output_string.append(char)
    return input_string, "".join(output_string)


def ser_key(key: str) -> str:
    if not all(char in KEY_CHARS for char in key):
        raise ValueError("Key contains disallowed characters")
    if key[0] not in KEY_START_CHARS:
        raise ValueError("Key does not start with allowed character")
    output = ""
    output += key
    return output


class StructuredFieldValue:
    def __init__(self) -> None:
        self.raw_value: str = None

    def parse(self, input_string: str) -> None:
        self.raw_value = input_string
        input_string = discard_ows(input_string)

        input_string = self.parse_content(input_string)  # type: ignore
        input_string = discard_ows(input_string)
        if input_string:
            raise ValueError(
                f"Trailing text after parsed value at: {input_string[:10]}"
            )

    def parse_content(self, input_string: str) -> str:
        raise NotImplementedError
