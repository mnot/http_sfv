
from typing import List, Tuple

from .item import parse_item, ser_item
from .util import discard_ows, remove_char


def parse_listlist(input_string: str) -> Tuple[str, List[List]]:
    top_list = []
    inner_list = []
    while input_string:
        input_string, item = parse_item(input_string)
        inner_list.append(item)
        input_string = discard_ows(input_string)
        if not input_string:
            top_list.append(inner_list)
            return input_string, top_list
        input_string, char = remove_char(input_string)
        if char == ",":
            top_list.append(inner_list)
            inner_list = []
        elif char != ";":
            raise ValueError("Trailing text after item in list.", input_string)
        input_string = discard_ows(input_string)
        if not input_string:
            raise ValueError("Trailing comma or semicolon at end of list.", input_string)
    raise ValueError("No List of Lists found.", input_string)


def ser_listlist(input_list: List[List]) -> str:
    output = ""
    count = len(input_list)
    for x in range(0, count):
        inner_list = input_list[x]
        if type(inner_list) != list:
            raise ValueError("Top-level list member is not a List.")
        inner_count = len(inner_list)
        for y in range(0, inner_count):
            inner_mem = inner_list[y]
            value = ser_item(inner_mem)
            output += value
            if y + 1 < inner_count:
                output += ";"
                output += " "
        if x + 1 < count:
            output += ","
            output += " "
    return output
