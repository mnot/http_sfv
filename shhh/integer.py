
from string import digits
from typing import Tuple, Union

from .util import remove_char

MAX_INT = 999999999999999
MIN_INT = -999999999999999

def parse_integer(input_string: str) -> Tuple[str, int]:
    return parse_number(input_string) # type: ignore

def ser_integer(inval: int) -> str:
    if type(inval) is not int:
        raise ValueError("Input is not an integer.")
    if not MIN_INT <= inval <= MAX_INT:
        raise ValueError("Input is out of Integer range.")
    output = ""
    if inval < 0:
        output += "-"
    output += str(abs(inval))
    return output



INTEGER = "integer"
FLOAT = "float"

def parse_number(input_string: str) -> Tuple[str, Union[int, float]]:
    _type = INTEGER
    _sign = 1
    input_number = ""
    if input_string and input_string[0] == "-":
        input_string = input_string[1:]
        _sign = -1
    if not input_string:
        raise ValueError("Number input lacked a number.", input_string)
    if not input_string[0] in digits:
        raise ValueError("Number doesn't start with a DIGIT.", input_string)
    while input_string:
        input_string, char = remove_char(input_string)
        if char in digits:
            input_number += char
        elif _type == INTEGER and char == ".":
            input_number += char
            _type = FLOAT
        else:
            input_string = char + input_string
            break
        if _type == INTEGER and len(input_number) > 15:
            raise ValueError("Integer too long.", input_string)
        if _type == FLOAT and len(input_number) > 16:
            raise ValueError("Float too long.", input_string)
    # we diverge from the specified algorithm a bit here to satisfy mypi.
    if _type == INTEGER:
        output_int = int(input_number) * _sign
        if not MIN_INT <= output_int <= MAX_INT:
            raise ValueError("Integer outside allowed range.", input_string)
        return input_string, output_int
    else:
        if input_number[-1] == ".":
            raise ValueError("Float ends in '.'.", input_string)
        if len(input_number.split(".", 1)[1]) > 6:
            raise ValueError("Float fractional component too long", input_string)
        output_float = float(input_number) * _sign # type: float
        return input_string, output_float
