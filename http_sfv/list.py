from typing import Tuple, Union, List, cast

from http_sfv.item import (
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
from http_sfv.types import ListType, ItemType, InnerListType, ItemOrInnerListType
from http_sfv.util import discard_http_ows
from http_sfv.util_binary import (
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


def bin_parse_list(data: bytes, cursor: int) -> Tuple[int, ListType]:
    _list = []
    cursor, member_count = decode_integer(data, cursor + 1)  # +1 for header
    for _ in range(member_count):
        cursor, member = bin_parse_item_or_inner_list(data, cursor)
        _list.append(member)
    return cursor, _list


def ser_list(_list: ListType) -> str:
    if len(_list) == 0:
        raise ValueError("No contents; field should not be emitted")
    return ", ".join([ser_item_or_inner_list(m) for m in _list])


def bin_ser_list(_list: ListType) -> bytes:
    data = [bin_header(STYPE.LIST)]
    data.append(encode_integer(len(_list)))
    for member in _list:
        data.append(bin_ser_item_or_inner_list(member))
    return b"".join(data)


def parse_item_or_inner_list(data: bytes) -> Tuple[int, Union[ItemType, InnerListType]]:
    try:
        if data[0] == PAREN_OPEN:
            return parse_innerlist(data)
    except IndexError:
        pass
    return parse_item(data)


def bin_parse_item_or_inner_list(
    data: bytes, cursor: int
) -> Tuple[int, Union[ItemType, InnerListType]]:
    if data[0] >> HEADER_OFFSET == STYPE.INNER_LIST:
        return bin_parse_innerlist(data, cursor)
    return bin_parse_item(data, cursor)


def ser_item_or_inner_list(thing: ItemOrInnerListType) -> str:
    if not isinstance(thing, tuple):
        thing = cast(ItemType, (thing, {}))
    if isinstance(cast(InnerListType, thing)[0], List):
        return ser_innerlist(cast(InnerListType, thing))
    return ser_item(cast(ItemType, thing))


def bin_ser_item_or_inner_list(thing: ItemOrInnerListType) -> bytes:
    if not isinstance(thing, tuple):
        thing = cast(ItemType, (thing, {}))
    if isinstance(cast(InnerListType, thing)[0], List):
        return bin_ser_innerlist(cast(InnerListType, thing))
    return bin_ser_item(cast(ItemType, thing))
