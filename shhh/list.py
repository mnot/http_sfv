
from typing import List, Tuple

from .item import parse_item, ser_item
from .util import discard_ows, remove_char


def parse_list(input_string: str) -> Tuple[str, List]:
    items = []
    while input_string:
        input_string, item = parse_item(input_string)
        items.append(item)
        input_string = discard_ows(input_string)
        if not input_string:
            return input_string, items
        input_string, char = remove_char(input_string)
        if char != ",":
            raise ValueError("Trailing text after item in list.", input_string)
        input_string = discard_ows(input_string)
        if not input_string:
            raise ValueError("Trailing comma at end of list.", input_string)
    raise ValueError("No List found.", input_string)


def ser_list(input_list: List) -> str:
    output = ""
    count = len(input_list)
    for x in range(0, count):
        mem = input_list[x]
        value = ser_item(mem)
        output += value
        if x + 1 < count:
            output += ","
            output += " "
    return output
