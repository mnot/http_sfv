from typing import Tuple

QUESTION = ord(b"?")
ONE = ord(b"1")
ZERO = ord(b"0")

_boolean_map = {ONE: (2, True), ZERO: (2, False)}


def parse_boolean(data: bytes) -> Tuple[int, bool]:
    try:
        return _boolean_map[data[1]]
    except KeyError:
        pass
    raise ValueError("No Boolean value found")


def ser_boolean(inval: bool) -> str:
    output = ""
    output += "?"
    if inval:
        output += "1"
    if not inval:
        output += "0"
    return output
