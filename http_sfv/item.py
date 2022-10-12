from typing import Tuple

from http_sfv.bare_item import (
    parse_bare_item,
    bin_parse_bare_item,
    ser_bare_item,
    bin_ser_bare_item,
)
from http_sfv.types import (
    BareItemType,
    ItemType,
    ParamsType,
)
from http_sfv.parameters import (
    parse_params,
    ser_params,
    bin_parse_params,
    bin_ser_params,
)
from http_sfv.util_binary import has_params

PAREN_OPEN = ord(b"(")
SEMICOLON = ord(b";")
EQUALS = ord(b"=")


def parse_item(data: bytes) -> Tuple[int, Tuple[BareItemType, ParamsType]]:
    try:
        bytes_consumed, value = parse_bare_item(data)
        param_bytes_consumed, params = parse_params(data[bytes_consumed:])
        bytes_consumed += param_bytes_consumed
    except Exception as why:
        raise ValueError from why
    return bytes_consumed, (value, params)


def bin_parse_item(
    data: bytes, cursor: int
) -> Tuple[int, Tuple[BareItemType, ParamsType]]:
    if has_params(data[cursor]):
        cursor, value = bin_parse_bare_item(data, cursor)
        cursor, parameters = bin_parse_params(data, cursor)
        return cursor, (value, parameters)
    cursor, value = bin_parse_bare_item(data, cursor)
    return cursor, (value, {})


def ser_item(item: ItemType) -> str:
    if not isinstance(item, tuple):
        item = (item, {})
    return f"{ser_bare_item(item[0])}{ser_params(item[1])}"


def bin_ser_item(item: ItemType) -> bytes:
    if not isinstance(item, tuple):
        item = (item, {})
    data = []
    if len(item[1]):
        data.append(bin_ser_bare_item(item[0], parameters=True))
        data.append(bin_ser_params(item[1]))
    else:
        data.append(bin_ser_bare_item(item[0]))
    return b"".join(data)
