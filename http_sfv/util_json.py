import base64
from typing import Any

from .token import Token


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