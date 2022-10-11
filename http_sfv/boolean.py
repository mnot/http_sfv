from typing import Tuple

from .util_binary import bin_header, extract_flags, STYPE

QUESTION = ord(b"?")
ONE = ord(b"1")
ZERO = ord(b"0")

_boolean_map = {ONE: (2, True), ZERO: (2, False)}


def parse_boolean(data: bytes) -> Tuple[int, bool]:
    try:
        return _boolean_map[data[1]]
    except (KeyError, IndexError):
        pass
    raise ValueError("No Boolean value found")


def ser_boolean(inval: bool) -> str:
    return f"?{inval and '1' or '0'}"


def bin_parse_boolean(data: bytes, cursor: int) -> Tuple[int, bool]:
    return cursor + 1, extract_flags(data[cursor])[0]  # +1 for header


def bin_ser_boolean(value: bool, parameters: bool) -> bytes:
    return bin_header(STYPE.BOOLEAN, parameters=parameters, flag1=value)
