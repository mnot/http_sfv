from decimal import Decimal
from typing import Tuple

from .integer import parse_number

INT_DIGITS = 12
FRAC_DIGITS = 3

def parse_decimal(input_string: str) -> Tuple[str, Decimal]:
    return parse_number(input_string)


def ser_decimal(input_decimal: Decimal) -> str:
    output = ""
    if input_decimal < 0:
        output += "-"
    abs_decimal = abs(input_decimal)
    integer_component = str(int(abs_decimal))
    output += integer_component
    if len(integer_component) > INT_DIGITS:
        raise ValueError("decimal with oversize integer component", integer_component)
    output += "."
    fractional_component = str(abs_decimal % 1)[2:]
    if len(fractional_component) > FRAC_DIGITS:
        fractional_remainder = fractional_component[FRAC_DIGITS + 1]
        if fractional_remainder == 5:
            fractional_tail = fractional_component[FRAC_DIGITS]
            if fractional_tail % 2:
                fractional_remainder = 10
            else:
                fractional_remainder = 0
        if fractional_remainder > 5:
            fractional_component = str(int(fractional_component[:FRAC_DIGITS]) + 1)
        elif fractional_remainder < 5:
            fractional_component = fractional_component[:FRAC_DIGITS]
    output += fractional_component
    return output
