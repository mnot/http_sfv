
from typing import List, Dict, Tuple

from .dictionary import parse_key, ser_key
from .identifier import parse_identifier, ser_identifier
from .item import parse_item, ser_item
from .util import discard_ows, remove_char


def parse_paramlist(input_string: str) -> Tuple[str, List]:
    items = []
    while input_string:
        input_string, item = parse_paramid(input_string)
        items.append(item)
        input_string = discard_ows(input_string)
        if not input_string:
            return input_string, items
        input_string, char = remove_char(input_string)
        if char != ",":
            raise ValueError("Trailing text after item in parameterised list.", input_string)
        input_string = discard_ows(input_string)
        if not input_string:
            raise ValueError("Trailing comma at end of parameterised list.", input_string)
    raise ValueError("No Parameterised List found.", input_string)


def parse_paramid(input_string: str) -> Tuple[str, Tuple[str, Dict]]:
    input_string, primary_identifier = parse_identifier(input_string)
    parameters = {}  # type: Dict
    while True:
        input_string = discard_ows(input_string)
        if not input_string or input_string[0] != ";":
            break
        input_string = input_string[1:]
        input_string = discard_ows(input_string)
        input_string, param_name = parse_key(input_string)
        if param_name in parameters:
            raise ValueError("Duplicate key in parameters.", input_string)
        param_value = None
        if input_string[0] == "=":
            input_string, char = remove_char(input_string)
            input_string, param_value = parse_item(input_string)
        parameters[param_name] = param_value
    return input_string, (primary_identifier, parameters)


def ser_paramlist(input_list: List) -> str:
    output = ""
    count = len(input_list)
    for x in range(0, count):
        (mem_id, mem_params) = input_list[x]
        _id = ser_identifier(mem_id)
        output += _id
        for param_name in mem_params:
            output += ";"
            name = ser_key(param_name)
            output += name
            if mem_params[param_name] is not None:
                value = ser_item(mem_params[param_name])
                output += "="
                output += value
        if x + 1 < count:
            output += ","
            output += " "
    return output
