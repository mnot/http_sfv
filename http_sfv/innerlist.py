from typing import Tuple, List, cast, Union

from http_sfv.item import (
    parse_item,
    bin_parse_item,
    ser_item,
    bin_ser_item,
)
from http_sfv.parameters import (
    parse_params,
    ser_params,
    bin_parse_params,
    bin_ser_params,
)
from http_sfv.types import (
    InnerListType,
    ItemType,
    ParamsType,
    ItemOrInnerListType,
)
from http_sfv.util import discard_ows
from http_sfv.util_binary import (
    encode_integer,
    decode_integer,
    bin_header,
    has_params,
    STYPE,
    HEADER_OFFSET,
)

PAREN_OPEN = ord(b"(")
PAREN_CLOSE = ord(b")")
INNERLIST_DELIMS = set(b" )")


def parse_innerlist(data: bytes) -> Tuple[int, InnerListType]:
    bytes_consumed = 1  # consume the "("
    inner_list: List[ItemType] = []
    params: ParamsType = {}
    while True:
        bytes_consumed += discard_ows(data[bytes_consumed:])
        if data[bytes_consumed] == PAREN_CLOSE:
            bytes_consumed += 1
            params_consumed, params = parse_params(data[bytes_consumed:])
            bytes_consumed += params_consumed
            return bytes_consumed, (inner_list, params)
        item_consumed, item = parse_item(data[bytes_consumed:])
        bytes_consumed += item_consumed
        inner_list.append(item)
        try:
            if data[bytes_consumed] not in INNERLIST_DELIMS:
                raise ValueError("Inner list bad delimitation")
        except IndexError as why:
            raise ValueError("End of inner list not found") from why


def bin_parse_innerlist(data: bytes, cursor: int) -> Tuple[int, InnerListType]:
    inner_list: List[ItemType] = []
    cursor, member_count = decode_integer(data, cursor + 1)  # +1 for header
    for _ in range(member_count):
        params = has_params(data[cursor])
        cursor, member = bin_parse_item(data, cursor)
        inner_list.append(member)
        if params:
            cursor, parameters = bin_parse_params(data, cursor)
        else:
            parameters = {}
    return cursor, (inner_list, parameters)


def ser_innerlist(inner_list: InnerListType) -> str:
    if not isinstance(inner_list, tuple):
        inner_list = (inner_list, {})
    return (
        f"({' '.join([ser_item(i) for i in inner_list[0]])}){ser_params(inner_list[1])}"
    )


def bin_ser_innerlist(inner_list: InnerListType) -> bytes:
    if not isinstance(inner_list, tuple):
        inner_list = (inner_list, {})
    params = bool(len(inner_list[1]))
    data = [bin_header(STYPE.INNER_LIST, parameters=params)]
    data.append(encode_integer(len(inner_list[0])))
    for member in inner_list[0]:
        data.append(bin_ser_item(member))
    if params:
        data.append(bin_ser_params(inner_list[1]))
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
