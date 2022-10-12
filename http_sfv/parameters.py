from typing import Tuple

from http_sfv.bare_item import (
    parse_bare_item,
    bin_parse_bare_item,
    ser_bare_item,
    bin_ser_bare_item,
)
from http_sfv.types import (
    BareItemType,
    ParamsType,
)
from http_sfv.util import (
    discard_ows,
    parse_key,
    ser_key,
)
from http_sfv.util_binary import (
    encode_integer,
    decode_integer,
    bin_header,
    STYPE,
)

PAREN_OPEN = ord(b"(")
SEMICOLON = ord(b";")
EQUALS = ord(b"=")


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
