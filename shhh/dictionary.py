
from collections import OrderedDict
from string import ascii_lowercase, digits
from typing import Dict, Tuple

from .item import parse_item, ser_item
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
        input_string, this_value = parse_item(input_string)
        dictionary[this_key] = this_value
        input_string = discard_ows(input_string)
        if not input_string:
            return input_string, dictionary
        input_string, char = remove_char(input_string)
        if char != ",":
            raise ValueError("Dictionary member trailing characters.", input_string)
        input_string = discard_ows(input_string)
        if not input_string:
            raise ValueError("Dictionary has trailing comma.", input_string)
    raise ValueError("No Dictionary found.")


def parse_key(input_string: str) -> Tuple[str, str]:
    if input_string[0] not in ascii_lowercase:
        raise ValueError("Key does not begin with lcalpha.", input_string)
    output_string = ""
    while input_string:
        input_string, char = remove_char(input_string)
        if char not in ascii_lowercase + digits + "_-":
            input_string = char + input_string
            return input_string, output_string
        output_string += char
    return input_string, output_string


def ser_dictionary(input_dict: Dict) -> str:
    output = ""
    members = list(input_dict.values())
    while members:
        member_name, member_value = members.pop(0)
        name = ser_key(member_name)
        output += name
        output += "="
        value = ser_item(member_value)
        output += value
        if members:
            output += ","
            output += " "
    return output


def ser_key(key: str) -> str:
    if type(key) is not str:
        raise ValueError("Key is not str.")
    if not all(char in ascii_lowercase + digits + "_-" for char in key):
        raise ValueError("Key contains disallowed characters.")
    output = ""
    output += key
    return output
