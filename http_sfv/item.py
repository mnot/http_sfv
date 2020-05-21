from decimal import Decimal
from string import ascii_lowercase, digits
from typing import Any, Tuple, List

from .util import remove_char, discard_ows
from .integer import parse_number, ser_integer, NUMBER_START_CHARS
from .decimal import ser_decimal
from .string import parse_string, ser_string, DQUOTE
from .byteseq import parse_byteseq, ser_byteseq, BYTE_DELIMIT
from .boolean import parse_boolean, ser_boolean
from .token import parse_token, ser_token, Token, TOKEN_START_CHARS

KEY_START_CHARS = set(ascii_lowercase + "*")
KEY_CHARS = set(ascii_lowercase + digits + "_-*.")


def parse_item(input_string: str) -> Tuple[str, Tuple[Any, dict]]:
    input_string, bare_item = parse_bare_item(input_string)
    input_string, parameters = parse_parameters(input_string)
    return input_string, (bare_item, parameters)


def parse_bare_item(input_string: str) -> Any:
    if not input_string:
        raise ValueError("Empty item.", input_string)
    start_char = input_string[0]
    if start_char in TOKEN_START_CHARS:
        return parse_token(input_string)
    if start_char is DQUOTE:
        return parse_string(input_string)
    if start_char in NUMBER_START_CHARS:
        return parse_number(input_string)
    if start_char is BYTE_DELIMIT:
        return parse_byteseq(input_string)
    if start_char == "?":
        return parse_boolean(input_string)
    raise ValueError(
        f"Item starting with '{input_string[0]}' can't be identified at: {input_string[:10]}"
    )


def parse_parameters(input_string: str) -> Tuple[str, dict]:
    parameters = {}
    while input_string:
        if input_string[0] != ";":
            break
        input_string, char = remove_char(input_string)
        input_string = discard_ows(input_string)
        input_string, param_name = parse_key(input_string)
        param_value = True
        if input_string and input_string[0] == "=":
            input_string, char = remove_char(input_string)
            input_string, param_value = parse_bare_item(input_string)
        parameters[param_name] = param_value
    return input_string, parameters


def parse_key(input_string: str) -> Tuple[str, str]:
    if input_string and input_string[0] not in KEY_START_CHARS:
        raise ValueError(
            f"Key does not begin with lcalpha or * at: {input_string[:10]}"
        )
    output_string = []  # type: List[str]
    while input_string:
        if input_string[0] not in KEY_CHARS:
            return input_string, "".join(output_string)
        input_string, char = remove_char(input_string)
        output_string.append(char)
    return input_string, "".join(output_string)


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
        return ser_decimal(item)
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
    if not all(char in KEY_CHARS for char in key):
        raise ValueError(f"Key contains disallowed characters")
    if key[0] not in KEY_START_CHARS:
        raise ValueError(f"Key does not start with allowed character")
    output = ""
    output += key
    return output
