import base64
from datetime import datetime
from decimal import Decimal
import json
from string import ascii_lowercase, ascii_uppercase, digits
from typing import Tuple, Any, Union

from .types import StructuredType, Token, DisplayString

SPACE = ord(b" ")
HTTP_OWS = set(b" \t")


def discard_ows(data: bytes) -> int:
    "Return the number of space characters at the beginning of data."
    i = 0
    ln = len(data)
    while True:
        if i == ln or data[i] != SPACE:
            return i
        i += 1


def discard_http_ows(data: bytes) -> int:
    "Return the number of space or HTAB characters at the beginning of data."
    i = 0
    ln = len(data)
    while True:
        if i == ln or data[i] not in HTTP_OWS:
            return i
        i += 1


KEY_START_CHARS = set((ascii_lowercase + "*").encode("ascii"))
KEY_CHARS = set((ascii_lowercase + digits + "_-*.").encode("ascii"))
UPPER_CHARS = set((ascii_uppercase).encode("ascii"))
COMPAT = False


def parse_key(data: bytes) -> Tuple[int, str]:
    if data == b"" or data[0] not in KEY_START_CHARS:
        if data == b"" or not (COMPAT and data[0] in UPPER_CHARS):
            raise ValueError("Key does not begin with lcalpha or *")
    bytes_consumed = 1
    while bytes_consumed < len(data):
        if data[bytes_consumed] not in KEY_CHARS:
            if not (COMPAT and data[bytes_consumed] in UPPER_CHARS):
                return bytes_consumed, data[:bytes_consumed].decode("ascii").lower()
        bytes_consumed += 1
    return bytes_consumed, data.decode("ascii").lower()


def ser_key(key: str) -> str:
    if not all(ord(char) in KEY_CHARS for char in key):
        raise ValueError("Key contains disallowed characters")
    if ord(key[0]) not in KEY_START_CHARS:
        raise ValueError("Key does not start with allowed character")
    return key


def to_json(structure: StructuredType, **args: Any) -> str:
    return json.dumps(structure, default=json_translate, **args)


def json_translate(inobj: Any) -> Union[Any, dict]:
    if isinstance(inobj, Token):
        return {"__type": "token", "value": str(inobj)}
    if isinstance(inobj, bytes):
        return {"__type": "binary", "value": base64.b32encode(inobj).decode("ascii")}
    if isinstance(inobj, datetime):
        return {"__type": "date", "value": inobj.timestamp()}
    if isinstance(inobj, DisplayString):
        return {"__type": "displaystring", "value": str(inobj)}
    if isinstance(inobj, Decimal):
        return float(inobj)
    raise ValueError(f"Unknown object type - {inobj}")
