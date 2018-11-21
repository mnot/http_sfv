
from string import ascii_lowercase, digits
from typing import Any, Tuple

from .integer import parse_number, ser_integer
from .float import ser_float
from .string import parse_string, ser_string, DQUOTE
from .byteseq import parse_byteseq, ser_byteseq
from .boolean import parse_boolean, ser_boolean
from .identifier import parse_identifier, ser_identifier

def parse_item(input_string: str) -> Tuple[str, Any]:
    if not input_string:
        raise ValueError("Empty item.", input_string)
    if input_string[0] in digits + '-':
        return parse_number(input_string)
    if input_string[0] == DQUOTE:
        return parse_string(input_string)
    if input_string[0] == "*":
        return parse_byteseq(input_string)
    if input_string[0] == "?":
        return parse_boolean(input_string)
    if input_string[0] in ascii_lowercase:
        return parse_identifier(input_string)
    raise ValueError("Item %s can't be identified.", input_string)

def ser_item(item: Any) -> str:
    item_type = type(item)
    if item_type not in [int, float, str, bytes, bool]:
        raise ValueError("Item type not recognised.")
    if item_type is int:
        return ser_integer(item)
    if item_type is float:
        return ser_float(item)
    if item_type is str:
        return ser_string(item)
    if item_type is str:
        return ser_identifier(item)
    if item_type is bool:
        return ser_boolean(item)
    return ser_byteseq(item)
