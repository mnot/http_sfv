from decimal import Decimal
from typing import Tuple

from http_sfv.boolean import parse_boolean, ser_boolean
from http_sfv.byteseq import parse_byteseq, ser_byteseq, BYTE_DELIMIT
from http_sfv.decimal import ser_decimal
from http_sfv.integer import parse_number, ser_integer, NUMBER_START_CHARS
from http_sfv.string import parse_string, ser_string, DQUOTE
from http_sfv.token import parse_token, ser_token, Token, TOKEN_START_CHARS
from http_sfv.types import BareItemType

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
