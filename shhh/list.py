from collections import OrderedDict
from typing import List, Tuple, Any

from .item import parse_item, ser_item, parse_parameters, ser_parameters
from .util import discard_ows, remove_char


def parse_list(input_string: str) -> Tuple[str, List]:
    members = []
    while input_string:
        input_string, member = parse_item_or_inner_list(input_string)
        members.append(member)
        input_string = discard_ows(input_string)
        if not input_string:
            return input_string, members
        input_string, char = remove_char(input_string)
        if char != ",":
            raise ValueError("Trailing text after item in list.", input_string)
        input_string = discard_ows(input_string)
        if not input_string:
            raise ValueError("Trailing comma at end of list.", input_string)
    return input_string, members


def parse_item_or_inner_list(input_string: str) -> Tuple[str, Any]:
    if input_string.startswith("("):
        return parse_inner_list(input_string)
    return parse_item(input_string)


def parse_inner_list(input_string: str) -> Tuple[str, Tuple[List, OrderedDict]]:
    input_string, char = remove_char(input_string)
    if char != "(":
        raise ValueError("First character of inner list is not (.", input_string)
    inner_list = []  # type: List
    while input_string:
        input_string = discard_ows(input_string)
        if input_string.startswith(")"):
            input_string = input_string[1:]
            input_string, parameters = parse_parameters(input_string)
            return input_string, (inner_list, parameters)
        input_string, item = parse_item(input_string)
        inner_list.append(item)
        if not (input_string.startswith(" ") or input_string.startswith(")")):
            raise ValueError("Inner list bad delimitation.", input_string)
    raise ValueError("End of inner list not found.", input_string)


def ser_list(input_list: List) -> str:
    output = ""
    count = len(input_list)
    for x in range(0, count):
        member_value, parameters = input_list[x]
        if member_value.isinstance(list):
            output += ser_inner_list(member_value, parameters)
        else:
            output += ser_item(member_value, parameters)
        if x + 1 < count:
            output += ","
            output += " "
    return output


def ser_inner_list(inner_list: List, list_parameters: OrderedDict) -> str:
    output = "("
    count = len(inner_list)
    for x in range(0, count):
        (member_value, parameters) = inner_list[x]
        output += ser_item(member_value, parameters)
        if x + 1 < count:
            output += " "
        output += ")"
        output += ser_parameters(list_parameters)
    return output
