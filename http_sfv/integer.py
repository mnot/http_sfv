from decimal import Decimal
from string import digits
from typing import Tuple, Union

from .util import remove_char

MAX_INT = 999999999999999
MIN_INT = -999999999999999

DIGITS = digits.encode("ascii")
NUMBER_START_CHARS = (digits + "-").encode("ascii")


def parse_integer(data: bytes) -> Tuple[int, int]:
    return parse_number(data)  # type: ignore


def ser_integer(inval: int) -> str:
    if not MIN_INT <= inval <= MAX_INT:
        raise ValueError("Input is out of Integer range.")
    output = ""
    if inval < 0:
        output += "-"
    output += str(abs(inval))
    return output


INTEGER = "integer"
DECIMAL = "decimal"


def parse_number(data: bytes) -> Tuple[int, Union[int, Decimal]]:
    _type = INTEGER
    _sign = 1
    input_number = []
    bytes_consumed = 0
    if data.startswith(b"-"):
        bytes_consumed += 1
        _sign = -1
    if not data[bytes_consumed:]:
        raise ValueError("Number input lacked a number")
    if not data[bytes_consumed : bytes_consumed + 1] in DIGITS:
        raise ValueError("Number doesn't start with a DIGIT")
    while bytes_consumed < len(data):
        offset, char = remove_char(data[bytes_consumed:])
        bytes_consumed += offset
        if char in DIGITS:
            input_number.append(char)
        elif _type is INTEGER and char == b".":
            if len(input_number) > 12:
                raise ValueError("Decimal too long.")
            input_number.append(char)
            _type = DECIMAL
        else:
            bytes_consumed -= 1
            break
        if _type == INTEGER and len(input_number) > 15:
            raise ValueError("Integer too long.")
        if _type == DECIMAL and len(input_number) > 16:
            raise ValueError("Decimal too long.")
    if _type == INTEGER:
        output_int = int(b"".join(input_number)) * _sign
        if not MIN_INT <= output_int <= MAX_INT:
            raise ValueError("Integer outside allowed range")
        return bytes_consumed, output_int
    if input_number and input_number[-1] == b".":
        raise ValueError("Decimal ends in '.'")
    if len(input_number) - input_number.index(b".") - 1 > 3:
        raise ValueError("Decimal fractional component too long")
    output_float = Decimal((b"".join(input_number)).decode("ascii")) * _sign
    return bytes_consumed, output_float
