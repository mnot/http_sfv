
from typing import Tuple

from .integer import parse_number

def parse_float(input_string: str) -> Tuple[str, float]:
    return parse_number(input_string)

def ser_float(inval: float) -> str:
    if type(inval) is not float:
        raise ValueError("Input is not a float.")
    output = ""
    output += "%f" % inval
    return output
