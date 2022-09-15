from typing import Tuple

from .util_binary import add_type, STYPE

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


def bin_parse_boolean(data: bytes) -> Tuple[int, bool]:
    """
    Payload: Integer l, b000 remaining bits, b indicating the Boolean value
    """
    return 1, (data[0] & 0b00010000) > 0


def bin_ser_boolean(value: bool) -> bytearray:
    if value:
        data = bytearray(b"\x10")
    else:
        data = bytearray(b"\x00")
    return add_type(data, STYPE.BOOLEAN)
