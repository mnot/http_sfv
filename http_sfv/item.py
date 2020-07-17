import base64
from decimal import Decimal
from string import ascii_lowercase, digits
from typing import Any, Tuple, List

from .util import StructuredFieldValue, remove_char, discard_ows
from .integer import parse_number, ser_integer, NUMBER_START_CHARS
from .decimal import ser_decimal
from .string import parse_string, ser_string, DQUOTE
from .byteseq import parse_byteseq, ser_byteseq, BYTE_DELIMIT
from .boolean import parse_boolean, ser_boolean
from .token import parse_token, ser_token, Token, TOKEN_START_CHARS

KEY_START_CHARS = set(ascii_lowercase + "*")
KEY_CHARS = set(ascii_lowercase + digits + "_-*.")


class Item(StructuredFieldValue):
    def __init__(self, value: Any = None) -> None:
        StructuredFieldValue.__init__(self)
        self.value = value
        self.params = Parameters()

    def parse_content(self, input_string: str) -> str:
        input_string, self.value = parse_bare_item(input_string)
        return self.params.parse(input_string)

    def __str__(self) -> str:
        output = ""
        output += ser_bare_item(self.value)
        output += str(self.params)
        return output

    def to_json(self) -> Any:
        value = value_to_json(self.value)
        return [value, self.params.to_json()]

    def from_json(self, json_data: Any) -> None:
        try:
            value, params = json_data
        except ValueError:
            raise ValueError(json_data)
        self.value = value_from_json(value)
        self.params.from_json(params)


class Parameters(dict):
    def parse(self, input_string: str) -> str:
        while input_string:
            if input_string[0] != ";":
                break
            input_string, _ = remove_char(input_string)
            input_string = discard_ows(input_string)
            input_string, param_name = parse_key(input_string)
            param_value = True
            if input_string and input_string[0] == "=":
                input_string, _ = remove_char(input_string)
                input_string, param_value = parse_bare_item(input_string)
            self[param_name] = param_value
        return input_string

    def __str__(self) -> str:
        output = ""
        for param_name in self:
            output += ";"
            output += ser_key(param_name)
            if self[param_name] is not True:
                output += "="
                output += ser_bare_item(self[param_name])
        return output

    def to_json(self) -> Any:
        return {k: value_to_json(v) for (k, v) in self.items()}

    def from_json(self, json_data: Any) -> None:
        for name, value in json_data.items():
            self[name] = value_from_json(value)


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


def ser_key(key: str) -> str:
    if not all(char in KEY_CHARS for char in key):
        raise ValueError(f"Key contains disallowed characters")
    if key[0] not in KEY_START_CHARS:
        raise ValueError(f"Key does not start with allowed character")
    output = ""
    output += key
    return output


def value_to_json(value: Any) -> Any:
    if isinstance(value, bytes):
        return {
            "__type": "binary",
            "value": base64.b32encode(value).decode("ascii"),
        }
    if isinstance(value, Token):
        return {"__type": "token", "value": value}
    return value


def value_from_json(value: Any) -> Any:
    if isinstance(value, dict):
        if "__type" in value:
            if value["__type"] == "token":
                return Token(value["value"])
            if value["__type"] == "binary":
                return base64.b32decode(value["value"])
            raise Exception(f"Unrecognised data type {value['__type']}")
        raise Exception(f"Dictionary as Item")
    return value
