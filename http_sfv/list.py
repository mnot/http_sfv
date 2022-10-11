from typing import Tuple, Union, List

from .item import (
    PAREN_OPEN,
    parse_item,
    parse_innerlist,
    bin_parse_item,
    bin_parse_innerlist,
    ser_item,
    bin_ser_item,
    ser_innerlist,
    bin_ser_innerlist,
)
from .types import ListType, ItemType, InnerListType, ItemOrInnerListType
from .util import discard_http_ows
from .util_binary import (
    encode_integer,
    decode_integer,
    bin_header,
    STYPE,
    HEADER_OFFSET,
)


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


def bin_parse_list(data: bytearray) -> Tuple[int, ListType]:
    bytes_consumed = 1  # header
    _list = []
    offset, member_count = decode_integer(data[bytes_consumed:])
    bytes_consumed += offset
    for _ in range(member_count):
        offset, member = bin_parse_item_or_inner_list(data[bytes_consumed:])
        bytes_consumed += offset
        _list.append(member)
    return bytes_consumed, _list


def ser_list(_list: ListType) -> str:
    if len(_list) == 0:
        raise ValueError("No contents; field should not be emitted")
    return ", ".join([ser_item_or_inner_list(m) for m in _list])


def bin_ser_list(_list: ListType) -> bytearray:
    data = bin_header(STYPE.LIST)
    data += encode_integer(len(_list))
    for member in _list:
        data += bin_ser_item_or_inner_list(member)
    return data


def parse_item_or_inner_list(data: bytes) -> Tuple[int, Union[ItemType, InnerListType]]:
    try:
        if data[0] == PAREN_OPEN:
            return parse_innerlist(data)
    except IndexError:
        pass
    return parse_item(data)


def bin_parse_item_or_inner_list(
    data: bytearray,
) -> Tuple[int, Union[ItemType, InnerListType]]:
    if data[0] >> HEADER_OFFSET == STYPE.INNER_LIST:
        return bin_parse_innerlist(data)
    return bin_parse_item(data)


def ser_item_or_inner_list(thing: ItemOrInnerListType) -> str:
    if isinstance(thing[0], List):
        return ser_innerlist(thing)
    return ser_item(thing)


def bin_ser_item_or_inner_list(thing: ItemOrInnerListType) -> bytearray:
    if isinstance(thing[0], List):
        return bin_ser_innerlist(thing)
    return bin_ser_item(thing)
