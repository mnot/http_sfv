from typing import Tuple


def parse_boolean(data: bytes) -> Tuple[int, bool]:
    if data[0:1] != b"?":
        raise ValueError("First character of Boolean is not '?'")
    if data[1:2] == b"1":
        return 2, True
    if data[1:2] == b"0":
        return 2, False
    raise ValueError("No Boolean value found")


def ser_boolean(inval: bool) -> str:
    output = ""
    output += "?"
    if inval:
        output += "1"
    if not inval:
        output += "0"
    return output
