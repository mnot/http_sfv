from string import ascii_letters, digits
from typing import Tuple

from .types import Token
from .util import remove_char

TOKEN_START_CHARS = (ascii_letters + "*").encode("ascii")
TOKEN_CHARS = (ascii_letters + digits + ":/!#$%&'*+-.^_`|~").encode("ascii")


def parse_token(data: bytes) -> Tuple[int, Token]:
    if not data or data[0:1] not in TOKEN_START_CHARS:
        raise ValueError("Token didn't start with legal character")
    bytes_consumed = 0
    while True:
        offset, char = remove_char(data[bytes_consumed:])
        if not char or char not in TOKEN_CHARS:
            return bytes_consumed, Token(data[:bytes_consumed].decode("ascii"))
        bytes_consumed += offset
    return bytes_consumed, Token(data[:bytes_consumed].decode("ascii"))


def ser_token(token: Token) -> str:
    if token and str(token[0]) not in TOKEN_START_CHARS.decode("ascii"):
        raise ValueError("Token didn't start with legal character")
    if not all(str(char) in TOKEN_CHARS.decode("ascii") for char in token):
        raise ValueError("Token contains disallowed characters")
    output = ""
    output += str(token)
    return output
