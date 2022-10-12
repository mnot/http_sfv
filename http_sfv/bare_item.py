from decimal import Decimal
from typing import Tuple

from http_sfv.boolean import (
    parse_boolean,
    ser_boolean,
    bin_parse_boolean,
    bin_ser_boolean,
)
from http_sfv.byteseq import (
    parse_byteseq,
    ser_byteseq,
    bin_parse_byteseq,
    bin_ser_byteseq,
    BYTE_DELIMIT,
)
from http_sfv.decimal import ser_decimal, bin_parse_decimal, bin_ser_decimal
from http_sfv.integer import (
    parse_number,
    ser_integer,
    bin_parse_integer,
    bin_ser_integer,
    NUMBER_START_CHARS,
)
from http_sfv.string import (
    parse_string,
    ser_string,
    bin_parse_string,
    bin_ser_string,
    DQUOTE,
)
from http_sfv.token import (
    parse_token,
    ser_token,
    bin_parse_token,
    bin_ser_token,
    Token,
    TOKEN_START_CHARS,
)
from http_sfv.types import BareItemType
from http_sfv.util_binary import STYPE, HEADER_OFFSET


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


def bin_ser_bare_item(  # pylint: disable=R0911
    item: BareItemType, parameters: bool = False
) -> bytes:
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
