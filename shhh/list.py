
from collections import OrderedDict
from string import ascii_lowercase, digits
from typing import List, Tuple, Any

from .item import parse_item, ser_item
from .util import discard_ows, remove_char


def parse_list(input_string: str) -> Tuple[str, List]:
    members = []
    while input_string:
        input_string, member = parse_param_member(input_string)
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


def parse_param_member(input_string: str) -> Tuple[str, Tuple[Any, OrderedDict]]:
    if input_string[0] == "(":
        input_string, member = parse_inner_list(input_string)
    else:
        input_string, member = parse_item(input_string)
    parameters = OrderedDict()   # type: OrderedDict
    while True:
        input_string = discard_ows(input_string)
        if not input_string or input_string[0] != ";":
            break
        input_string, char = remove_char(input_string)
        input_string = discard_ows(input_string)
        input_string, param_name = parse_key(input_string)
        if param_name in parameters:
            raise ValueError(f"Duplicate name '{param_name}' in paramemter.", input_string)
        param_value = None
        if input_string and input_string[0] == "=":
            input_string, char = remove_char(input_string)
            input_string, param_value = parse_item(input_string)
        parameters[param_name] = param_value
    return input_string, (member, parameters)


def parse_inner_list(input_string: str) -> Tuple[str, List]:
    input_string, char = remove_char(input_string)
    if char != "(":
        raise ValueError("First character of inner list is not (", input_string)
    inner_list = []  # type: List
    while input_string:
        input_string = discard_ows(input_string)
        if input_string and input_string[0] == ")":
            input_string, char = remove_char(input_string)
            return input_string, inner_list
        input_string, item = parse_item(input_string)
        inner_list.append(item)
        if not input_string or input_string[0] not in [" ", ")"]:
            raise ValueError("Inner list items not separated by a space.", input_string)
    raise ValueError("End of inner list not found.", input_string)


def parse_key(input_string: str) -> Tuple[str, str]:
    if input_string[0] not in ascii_lowercase:
        raise ValueError("Key does not begin with lcalpha.", input_string)
    output_string = ""
    while input_string:
        input_string, char = remove_char(input_string)
        if char not in ascii_lowercase + digits + "_-*":
            input_string = char + input_string
            return input_string, output_string
        output_string += char
    return input_string, output_string


def ser_list(input_list: List) -> str:
    output = ""
    count = len(input_list)
    for x in range(0, count):
        member, parameters = input_list[x]
        if member.isinstance(list):
            mem_value = ser_inner_list(member)
        else:
            mem_value = ser_item(member)
        output += mem_value
        output += ser_parameters(parameters)
        if x + 1 < count:
            output += ","
            output += " "
    return output


def ser_inner_list(inner_list: List) -> str:
    output = "("
    count = len(inner_list)
    for x in range(0, count):
        mem = inner_list[x]
        value = ser_item(mem)
        output += value
        if x + 1 < count:
            output += " "
        output += ")"
    return output


def ser_parameters(parameters: OrderedDict) -> str:
    output = ""
    for param_name in parameters:
        output += ";"
        name = ser_key(param_name)
        output += name
        if parameters[param_name] != None:
            value = ser_item(parameters[param_name])
            output += "="
            output += value
    return output


def ser_key(key: str) -> str:
    if not isinstance(key, str):
        raise ValueError("Key is not str.")
    if not all(char in ascii_lowercase + digits + "_-*" for char in key):
        raise ValueError("Key contains disallowed characters.")
    output = ""
    output += key
    return output
