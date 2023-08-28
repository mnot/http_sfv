from typing import Tuple

from http_sfv.bare_item import parse_bare_item, ser_bare_item
from http_sfv.types import BareItemType, ItemType, ParamsType
from http_sfv.parameters import parse_params, ser_params

PAREN_OPEN = ord(b"(")
SEMICOLON = ord(b";")
EQUALS = ord(b"=")


def parse_item(data: bytes) -> Tuple[int, Tuple[BareItemType, ParamsType]]:
    bytes_consumed, value = parse_bare_item(data)
    param_bytes_consumed, params = parse_params(data[bytes_consumed:])
    bytes_consumed += param_bytes_consumed
    return bytes_consumed, (value, params)


def ser_item(item: ItemType) -> str:
    if not isinstance(item, tuple):
        item = (item, {})
    return f"{ser_bare_item(item[0])}{ser_params(item[1])}"
