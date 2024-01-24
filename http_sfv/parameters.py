from typing import Tuple

from http_sfv.bare_item import parse_bare_item, ser_bare_item
from http_sfv.types import BareItemType, ParamsType
from http_sfv.util import discard_ows, parse_key, ser_key

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


def ser_params(params: ParamsType) -> str:
    return "".join(
        [
            f";{ser_key(k)}{f'={ser_bare_item(v)}' if v is not True else ''}"
            for k, v in params.items()
        ]
    )
