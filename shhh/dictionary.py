
from collections import OrderedDict
from typing import Tuple

from .item import ser_item
from .list import parse_key, ser_key, ser_inner_list, parse_param_member, ser_parameters
from .util import remove_char, discard_ows

def parse_dictionary(input_string: str) -> Tuple[str, OrderedDict]:
    dictionary = OrderedDict()  # type: OrderedDict
    while input_string:
        input_string, this_key = parse_key(input_string)
        if this_key in dictionary:
            raise ValueError("Duplicate dictionary key.", input_string)
        input_string, char = remove_char(input_string)
        if char != "=":
            raise ValueError("Dictionary key not followed by '='.", input_string)
        input_string, member = parse_param_member(input_string)
        dictionary[this_key] = member
        input_string = discard_ows(input_string)
        if not input_string:
            return input_string, dictionary
        input_string, char = remove_char(input_string)
        if char != ",":
            raise ValueError("Dictionary member trailing characters.", input_string)
        input_string = discard_ows(input_string)
        if not input_string:
            raise ValueError("Dictionary has trailing comma.", input_string)
    return input_string, dictionary



def ser_dictionary(input_dict: OrderedDict) -> str:
    output = ""
    members = list(input_dict.items())
    while members:
        member_name, (member_value, parameters) = members.pop(0)
        name = ser_key(member_name)
        output += name
        output += "="
        if member_value.isinstance(list):
            value = ser_inner_list(member_value)
        else:
            value = ser_item(member_value)
        output += value
        output += ser_parameters(parameters)
        if members:
            output += ","
            output += " "
    return output
