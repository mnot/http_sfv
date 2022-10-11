from decimal import Decimal
from typing import Tuple, List


from .boolean import parse_boolean, ser_boolean, bin_parse_boolean, bin_ser_boolean
from .byteseq import (
    parse_byteseq,
    ser_byteseq,
    bin_parse_byteseq,
    bin_ser_byteseq,
    BYTE_DELIMIT,
)
from .decimal import ser_decimal, bin_parse_decimal, bin_ser_decimal
from .integer import (
    parse_number,
    ser_integer,
    bin_parse_integer,
    bin_ser_integer,
    NUMBER_START_CHARS,
)
from .string import parse_string, ser_string, bin_parse_string, bin_ser_string, DQUOTE
from .token import (
    parse_token,
    ser_token,
    bin_parse_token,
    bin_ser_token,
    Token,
    TOKEN_START_CHARS,
)
from .types import (
    BareItemType,
    InnerListType,
    ItemType,
    ParamsType,
)
from .util import (
    discard_ows,
    parse_key,
    ser_key,
)
from .util_binary import (
    encode_integer,
    decode_integer,
    bin_header,
    has_params,
    STYPE,
    HEADER_OFFSET,
)


SEMICOLON = ord(b";")
EQUALS = ord(b"=")
PAREN_OPEN = ord(b"(")
PAREN_CLOSE = ord(b")")
INNERLIST_DELIMS = set(b" )")


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
    return f"{ser_bare_item(item[0])}{ser_params(item[1])}"


def bin_ser_item(item: ItemType) -> bytes:
    data = []
    if len(item[1]):
        data.append(bin_ser_bare_item(item[0], parameters=True))
        data.append(bin_ser_params(item[1]))
    else:
        data.append(bin_ser_bare_item(item[0]))
    return b"".join(data)


def parse_params(data: bytes) -> Tuple[int, ParamsType]:
    bytes_consumed = 0
    params = {}
    while True:
        try:
            if data[bytes_consumed] != SEMICOLON:
                break
        except IndexError:
            break
        bytes_consumed += 1  # consume the ";"
        bytes_consumed += discard_ows(data[bytes_consumed:])
        offset, param_name = parse_key(data[bytes_consumed:])
        bytes_consumed += offset
        param_value: BareItemType = True
        try:
            if data[bytes_consumed] == EQUALS:
                bytes_consumed += 1  # consume the "="
                offset, param_value = parse_bare_item(data[bytes_consumed:])
                bytes_consumed += offset
        except IndexError:
            pass
        params[param_name] = param_value
    return bytes_consumed, params


def bin_parse_params(data: bytes, cursor: int) -> Tuple[int, ParamsType]:
    params = {}
    cursor, member_count = decode_integer(data, cursor + 1)  # +1 for header
    for _ in range(member_count):
        key_len = data[cursor]
        cursor += 1
        key_end = cursor + key_len
        key = data[cursor:key_end].decode("ascii")
        cursor = key_end
        cursor, value = bin_parse_bare_item(data, cursor)
        params[key] = value
    return cursor, params


def ser_params(params: ParamsType) -> str:
    return "".join(
        [
            f";{ser_key(k)}{f'={ser_bare_item(v)}' if v is not True else ''}"
            for k, v in params.items()
        ]
    )


def bin_ser_params(params: ParamsType) -> bytes:
    data = [bin_header(STYPE.PARAMETER)]
    data.append(encode_integer(len(params)))
    for member in params:
        data.append(len(member).to_bytes(1, "big"))
        data.append(member.encode("ascii"))
        data.append(bin_ser_bare_item(params[member]))
    return b"".join(data)


def parse_innerlist(data: bytes) -> Tuple[int, InnerListType]:
    bytes_consumed = 1  # consume the "("
    inner_list: List[ItemType] = []
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
        return bytes_consumed, (inner_list, params)


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
    return (
        f"({' '.join([ser_item(i) for i in inner_list[0]])}){ser_params(inner_list[1])}"
    )


def bin_ser_innerlist(inner_list: InnerListType) -> bytes:
    params = bool(len(inner_list[1]))
    data = [bin_header(STYPE.INNER_LIST, parameters=params)]
    data.append(encode_integer(len(inner_list[0])))
    for member in inner_list[0]:
        data.append(bin_ser_item(member))
    if params:
        data.append(bin_ser_params(inner_list[1]))
    return b"".join(data)


_parse_map = {
    DQUOTE: parse_string,
    BYTE_DELIMIT: parse_byteseq,
    ord(b"?"): parse_boolean,
}
for c in TOKEN_START_CHARS:
    _parse_map[c] = parse_token
for c in NUMBER_START_CHARS:
    _parse_map[c] = parse_number


def parse_bare_item(data: bytes) -> Tuple[int, BareItemType]:
    if not data:
        raise ValueError("Empty item")
    try:
        return _parse_map[data[0]](data)  # type: ignore
    except KeyError as why:
        raise ValueError(
            f"Item starting with '{data[0:1].decode('ascii')}' can't be identified"
        ) from why


_bin_parse_map = {
    STYPE.INTEGER: bin_parse_integer,
    STYPE.DECIMAL: bin_parse_decimal,
    STYPE.STRING: bin_parse_string,
    STYPE.TOKEN: bin_parse_token,
    STYPE.BYTESEQ: bin_parse_byteseq,
    STYPE.BOOLEAN: bin_parse_boolean,
}


def bin_parse_bare_item(data: bytes, cursor: int) -> Tuple[int, BareItemType]:
    try:
        return _bin_parse_map[data[cursor] >> HEADER_OFFSET](data, cursor)  # type: ignore
    except KeyError as why:
        raise ValueError(
            f"Item with type '{data[cursor] >> HEADER_OFFSET}' can't be identified"
        ) from why


_ser_map = {
    int: ser_integer,
    float: ser_decimal,
    str: ser_string,
    bool: ser_boolean,
    bytes: ser_byteseq,
}


def ser_bare_item(item: BareItemType) -> str:
    try:
        return _ser_map[type(item)](item)  # type: ignore
    except KeyError:
        pass
    if isinstance(item, Token):
        return ser_token(item)
    if isinstance(item, Decimal):
        return ser_decimal(item)
    raise ValueError(f"Can't serialise; unrecognised item with type {type(item)}")


def bin_ser_bare_item(item: BareItemType, parameters: bool = False) -> bytes:
    if isinstance(item, bool):
        return bin_ser_boolean(item, parameters)
    if isinstance(item, int):
        return bin_ser_integer(item, parameters)
    if isinstance(item, float):
        return bin_ser_decimal(Decimal(item), parameters)
    if isinstance(item, str):
        return bin_ser_string(item, parameters)
    if isinstance(item, bytes):
        return bin_ser_byteseq(item, parameters)
    if isinstance(item, Token):
        return bin_ser_token(item, parameters)
    if isinstance(item, Decimal):
        return bin_ser_decimal(item, parameters)
    raise ValueError(f"Can't serialise; unrecognised item with type {type(item)}.")
