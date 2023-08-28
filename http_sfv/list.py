from typing import Tuple

from http_sfv.innerlist import parse_item_or_inner_list, ser_item_or_inner_list
from http_sfv.types import ListType
from http_sfv.util import discard_http_ows


COMMA = ord(b",")


def parse_list(data: bytes) -> Tuple[int, ListType]:
    bytes_consumed = 0
    _list = []
    data_len = len(data)
    while True:
        offset, member = parse_item_or_inner_list(data[bytes_consumed:])
        bytes_consumed += offset
        _list.append(member)
        bytes_consumed += discard_http_ows(data[bytes_consumed:])
        if bytes_consumed == data_len:
            return bytes_consumed, _list
        if data[bytes_consumed] != COMMA:
            raise ValueError("Trailing text after item in list")
        bytes_consumed += 1
        bytes_consumed += discard_http_ows(data[bytes_consumed:])
        if bytes_consumed == data_len:
            raise ValueError("Trailing comma at end of list")


def ser_list(_list: ListType) -> str:
    if len(_list) == 0:
        raise ValueError("No contents; field should not be emitted")
    return ", ".join([ser_item_or_inner_list(m) for m in _list])
