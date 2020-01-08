from decimal import Decimal
from string import ascii_letters, ascii_lowercase, digits
from typing import Any, Tuple

from .util import remove_char, discard_ows
from .integer import parse_number, ser_integer
from .float import ser_float
from .string import parse_string, ser_string, DQUOTE
from .byteseq import parse_byteseq, ser_byteseq, BYTE_DELIMIT
from .boolean import parse_boolean, ser_boolean
from .token import parse_token, ser_token, Token


def parse_item(input_string: str) -> Tuple[str, Tuple[Any, dict]]:
    input_string, bare_item = parse_bare_item(input_string)
    input_string, parameters = parse_parameters(input_string)
    return input_string, (bare_item, parameters)


def parse_bare_item(input_string: str) -> Any:
    if not input_string:
        raise ValueError("Empty item.", input_string)
    if input_string[0] in digits + "-":
        return parse_number(input_string)
    if input_string.startswith(DQUOTE):
        return parse_string(input_string)
    if input_string.startswith(BYTE_DELIMIT):
        return parse_byteseq(input_string)
    if input_string.startswith("?"):
        return parse_boolean(input_string)
    if input_string[0] in ascii_letters:
        return parse_token(input_string)
    raise ValueError(
        "Item starting with '%s' can't be identified." % input_string[0], input_string
    )


def parse_parameters(input_string: str) -> Tuple[str, dict]:
    parameters = {}
    while input_string:
        if input_string[0] != ";":
            break
        input_string, char = remove_char(input_string)
        input_string = discard_ows(input_string)
        input_string, param_name = parse_key(input_string)
        if param_name in parameters:
            raise ValueError(
                f"Duplicate name '{param_name}' in paramemter.", input_string
            )
        param_value = True
        if input_string.startswith("="):
            input_string, char = remove_char(input_string)
            input_string, param_value = parse_bare_item(input_string)
        parameters[param_name] = param_value
    return input_string, parameters


def parse_key(input_string: str) -> Tuple[str, str]:
    if input_string[0] not in ascii_lowercase:
        raise ValueError("Key does not begin with lcalpha.", input_string)
    output_string = ""
    while input_string:
        if input_string[0] not in ascii_lowercase + digits + "_-*":
            return input_string, output_string
        input_string, char = remove_char(input_string)
        output_string += char
    return input_string, output_string


def ser_item(item: Any, item_parameters: dict) -> str:
    output = ""
    output += ser_bare_item(item)
    output += ser_parameters(item_parameters)
    return output


def ser_bare_item(item: Any) -> str:
    item_type = type(item)
    if item_type is int:
        return ser_integer(item)
    if isinstance(item, Decimal):
        return ser_float(item)
    if isinstance(item, Token):
        return ser_token(item)
    if item_type is str:
        return ser_string(item)
    if item_type is bool:
        return ser_boolean(item)
    if item_type is bytes:
        return ser_byteseq(item)
    raise ValueError(f"Can't serialise; unrecognised item with type {item_type}")


def ser_parameters(parameters: dict) -> str:
    output = ""
    for param_name in parameters:
        param_value = parameters[param_name]
        output += ";"
        output += ser_key(param_name)
        if param_value is not True:
            output += "="
            output += ser_bare_item(param_value)
    return output


def ser_key(key: str) -> str:
    if not all(char in ascii_lowercase + digits + "_-*" for char in key):
        raise ValueError("Key contains disallowed characters.")
    output = ""
    output += key
    return output
