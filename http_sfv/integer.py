from decimal import Decimal
from string import digits
from typing import Tuple, Union

from .util import remove_char

MAX_INT = 999999999999999
MIN_INT = -999999999999999

NUMBER_START_CHARS = set(digits + "-")


def parse_integer(input_string: str) -> Tuple[str, int]:
    return parse_number(input_string)  # type: ignore


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


def parse_number(input_string: str) -> Tuple[str, Union[int, Decimal]]:
    _type = INTEGER
    _sign = 1
    input_number = []
    if input_string.startswith("-"):
        input_string = input_string[1:]
        _sign = -1
    if not input_string:
        raise ValueError("Number input lacked a number at: {input_string[:10]}")
    if not input_string[0] in digits:
        raise ValueError("Number doesn't start with a DIGIT at: {input_string[:10]}")
    while input_string:
        input_string, char = remove_char(input_string)
        if char in digits:
            input_number.append(char)
        elif _type is INTEGER and char == ".":
            if len(input_number) > 12:
                raise ValueError("Decimal too long.", "".join(input_number))
            input_number.append(char)
            _type = DECIMAL
        else:
            input_string = char + input_string
            break
        if _type == INTEGER and len(input_number) > 15:
            raise ValueError("Integer too long.", input_string)
        if _type == DECIMAL and len(input_number) > 16:
            raise ValueError("Decimal too long.", input_string)
    # we diverge from the specified algorithm a bit here to satisfy mypi.
    if _type == INTEGER:
        output_int = int("".join(input_number)) * _sign
        if not MIN_INT <= output_int <= MAX_INT:
            raise ValueError("Integer outside allowed range at: {input_string[:10]}")
        return input_string, output_int
    if input_number and input_number[-1] == ".":
        raise ValueError("Decimal ends in '.'.", input_string)
    if len(input_number) - input_number.index(".") - 1 > 3:
        raise ValueError(
            "Decimal fractional component too long at: {input_string[:10]}"
        )
    output_float = Decimal("".join(input_number)) * _sign
    return input_string, output_float
