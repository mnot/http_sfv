from string import ascii_letters, digits
from typing import Tuple

from .types import Token
from .util_binary import decode_integer, encode_integer, bin_header, STYPE


TOKEN_START_CHARS = set((ascii_letters + "*").encode("ascii"))
TOKEN_CHARS = set((ascii_letters + digits + ":/!#$%&'*+-.^_`|~").encode("ascii"))


def parse_token(data: bytes) -> Tuple[int, Token]:
    bytes_consumed = 1  # consume start char
    size = len(data)
    while bytes_consumed < size:
        if data[bytes_consumed] not in TOKEN_CHARS:
            return bytes_consumed, Token(data[:bytes_consumed].decode("ascii"))
        bytes_consumed += 1
    return bytes_consumed, Token(data[:bytes_consumed].decode("ascii"))


def ser_token(token: Token) -> str:
    if token and ord(str(token)[0]) not in TOKEN_START_CHARS:
        raise ValueError("Token didn't start with legal character")
    if not all(ord(char) in TOKEN_CHARS for char in str(token)):
        raise ValueError("Token contains disallowed characters")
    return str(token)


def bin_parse_token(data: bytes, cursor: int) -> Tuple[int, Token]:
    cursor, length = decode_integer(data, cursor + 1)  # +1 for header
    end = cursor + length
    return end, Token(data[cursor:end].decode("ascii"))


def bin_ser_token(value: Token, parameters: bool) -> bytes:
    data = [bin_header(STYPE.TOKEN, parameters=parameters)]
    data.append(encode_integer(len(value)))
    data.append(value.encode("ascii"))
    return b"".join(data)
