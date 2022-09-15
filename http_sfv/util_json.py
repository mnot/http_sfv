import base64
from decimal import Decimal

from .token import Token
from .types import BareItemType, JsonBareType


def value_to_json(value: BareItemType) -> JsonBareType:
    if isinstance(value, bytes):
        return {
            "__type": "binary",
            "value": base64.b32encode(value).decode("ascii"),
        }
    if isinstance(value, Token):
        return {"__type": "token", "value": str(value)}
    if isinstance(value, Decimal):
        return float(value)
    return value


def value_from_json(value: JsonBareType) -> BareItemType:
    if isinstance(value, dict):
        if "__type" in value:
            if value["__type"] == "token":
                return Token(value["value"])
            if value["__type"] == "binary":
                return base64.b32decode(value["value"])
            raise Exception(f"Unrecognised data type {value['__type']}")
        raise Exception("Dictionary as Item")
    return value
