from string import ascii_lowercase, digits
from typing import Tuple


def next_char(data: bytes) -> bytes:
    """Return the next character in data, or nothing if it is not there."""
    return data[0:1]


def remove_char(data: bytes) -> Tuple[int, bytes]:
    "Remove the first character of input_string and return it."
    if not data:
        return 0, b""
    return 1, data[0:1]


def discard_ows(data: bytes) -> int:
    "Return the number of space characters at the beginning of data."
    i = 0
    l = len(data)
    while True:
        if i == l or data[i : i + 1] != b" ":
            return i
        i += 1


def discard_http_ows(data: bytes) -> int:
    "Return the number of space or HTAB characters at the beginning of data."
    i = 0
    l = len(data)
    while True:
        if i == l or data[i : i + 1] not in b" \t":
            return i
        i += 1


KEY_START_CHARS = (ascii_lowercase + "*").encode("ascii")
KEY_CHARS = (ascii_lowercase + digits + "_-*.").encode("ascii")


def parse_key(data: bytes) -> Tuple[int, str]:
    bytes_consumed = 0
    peek = next_char(data)
    if not peek or peek not in KEY_START_CHARS:
        raise ValueError("Key does not begin with lcalpha or *")
    while True:
        peek = next_char(data[bytes_consumed:])
        if not peek or peek not in KEY_CHARS:
            return bytes_consumed, data[:bytes_consumed].decode("ascii")
        bytes_consumed += 1


def ser_key(key: str) -> str:
    if not all(char.encode("ascii") in KEY_CHARS for char in key):
        raise ValueError("Key contains disallowed characters")
    if key[0].encode("ascii") not in KEY_START_CHARS:
        raise ValueError("Key does not start with allowed character")
    output = ""
    output += key
    return output


class StructuredFieldValue:
    def __init__(self) -> None:
        self.raw_value: bytes = None

    def parse(self, data: bytes) -> None:
        self.raw_value = data
        bytes_consumed = discard_ows(bytearray(data))
        bytes_consumed += self.parse_content(data[bytes_consumed:])  # type: ignore
        bytes_consumed += discard_ows(data[bytes_consumed:])
        if data[bytes_consumed:]:
            raise ValueError("Trailing text after parsed value")

    def parse_content(self, data: bytes) -> int:
        raise NotImplementedError
