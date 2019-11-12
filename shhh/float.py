from decimal import Decimal
from typing import Tuple

from .integer import parse_number


def parse_float(input_string: str) -> Tuple[str, float]:
    return parse_number(input_string)


def ser_float(input_float: float) -> str:
    output = ""
    if input_float < 0:
        output += "-"
    integer_component = int(input_float)
    output += str(integer_component)
    integer_digits = len(str(integer_component))
    if integer_digits > 14:
        raise ValueError("Float with more than 14 integer digits", input_float)
    digits_avail = 15 - integer_digits
    fractional_digits_avail = min(digits_avail, 6)
    output += "."
    fractional_component = str(Decimal(input_float).remainder_near(1))[2:]
    output += fractional_component[:fractional_digits_avail]
    return output
