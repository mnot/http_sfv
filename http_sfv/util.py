from string import ascii_lowercase, digits
from typing import Tuple

SPACE = ord(b" ")
HTTP_OWS = set(b" \t")


def discard_ows(data: bytes) -> int:
    "Return the number of space characters at the beginning of data."
    i = 0
    l = len(data)
    while True:
        if i == l or data[i] != SPACE:
            return i
        i += 1


def discard_http_ows(data: bytes) -> int:
    "Return the number of space or HTAB characters at the beginning of data."
    i = 0
    l = len(data)
    while True:
        if i == l or data[i] not in HTTP_OWS:
            return i
        i += 1


KEY_START_CHARS = set((ascii_lowercase + "*").encode("ascii"))
KEY_CHARS = set((ascii_lowercase + digits + "_-*.").encode("ascii"))


def parse_key(data: bytes) -> Tuple[int, str]:
    if data == b"" or data[0] not in KEY_START_CHARS:
        raise ValueError("Key does not begin with lcalpha or *")
    bytes_consumed = 1
    while bytes_consumed < len(data):
        if data[bytes_consumed] not in KEY_CHARS:
            return bytes_consumed, data[:bytes_consumed].decode("ascii")
        bytes_consumed += 1
    return bytes_consumed, data.decode("ascii")


def ser_key(key: str) -> str:
    if not all(ord(char) in KEY_CHARS for char in key):
        raise ValueError("Key contains disallowed characters")
    if ord(key[0]) not in KEY_START_CHARS:
        raise ValueError("Key does not start with allowed character")
    return key


class StructuredFieldValue:
    def parse(self, data: bytes) -> None:
        bytes_consumed = discard_ows(data)
        bytes_consumed += self.parse_content(data[bytes_consumed:])  # type: ignore
        bytes_consumed += discard_ows(data[bytes_consumed:])
        if data[bytes_consumed:]:
            raise ValueError("Trailing text after parsed value")

    def parse_content(self, data: bytes) -> int:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError
