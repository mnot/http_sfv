from collections import UserList
from decimal import Decimal
from typing import List as _List, Tuple, Union, Any, Iterable, cast

from .boolean import parse_boolean, ser_boolean
from .byteseq import parse_byteseq, ser_byteseq, BYTE_DELIMIT
from .decimal import ser_decimal
from .integer import parse_number, ser_integer, NUMBER_START_CHARS
from .string import parse_string, ser_string, DQUOTE
from .token import parse_token, ser_token, Token, TOKEN_START_CHARS
from .types import BareItemType, JsonType
from .util import (
    StructuredFieldValue,
    discard_ows,
    parse_key,
    ser_key,
)
from .util_json import value_to_json, value_from_json


class Item(StructuredFieldValue):
    def __init__(self, value: BareItemType = None) -> None:
        StructuredFieldValue.__init__(self)
        self.value = value
        self.params = Parameters()

    def parse_content(self, data: bytes) -> int:
        bytes_consumed, self.value = parse_bare_item(data)
        bytes_consumed += self.params.parse(data[bytes_consumed:])
        return bytes_consumed

    def __str__(self) -> str:
        output = ""
        output += ser_bare_item(self.value)
        output += str(self.params)
        return output

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Item):
            return self.value == other.value
        return self.value == other

    def to_json(self) -> JsonType:
        value = value_to_json(self.value)
        return [value, self.params.to_json()]

    def from_json(self, json_data: JsonType) -> None:
        try:
            value, params = json_data
        except ValueError:
            raise ValueError(json_data)
        self.value = value_from_json(value)
        self.params.from_json(params)


class Parameters(dict):
    def parse(self, data: bytes) -> int:
        bytes_consumed = 0
        while True:
            if data[bytes_consumed : bytes_consumed + 1] != b";":
                break
            bytes_consumed += 1  # consume the ";"
            bytes_consumed += discard_ows(data[bytes_consumed:])
            offset, param_name = parse_key(data[bytes_consumed:])
            bytes_consumed += offset
            param_value: BareItemType = True
            if data[bytes_consumed : bytes_consumed + 1] == b"=":
                bytes_consumed += 1  # consume the "="
                offset, param_value = parse_bare_item(data[bytes_consumed:])
                bytes_consumed += offset
            self[param_name] = param_value
        return bytes_consumed

    def __str__(self) -> str:
        output = ""
        for param_name in self:
            output += ";"
            output += ser_key(param_name)
            if self[param_name] is not True:
                output += "="
                output += ser_bare_item(self[param_name])
        return output

    def to_json(self) -> JsonType:
        return {k: value_to_json(v) for (k, v) in self.items()}

    def from_json(self, json_data: JsonType) -> None:
        for name, value in json_data.items():
            self[name] = value_from_json(value)


SingleItemType = Union[BareItemType, Item]


class InnerList(UserList):
    def __init__(self, values: _List[Union[Item, SingleItemType]] = None) -> None:
        UserList.__init__(self, [itemise(v) for v in values or []])
        self.params = Parameters()

    def parse(self, data: bytes) -> int:
        if data[0:1] != b"(":
            raise ValueError("First character of inner list is not '('")
        bytes_consumed = 1  # consume the "("
        while True:
            bytes_consumed += discard_ows(data[bytes_consumed:])
            if data[bytes_consumed : bytes_consumed + 1] == b")":
                bytes_consumed += 1
                bytes_consumed += self.params.parse(data[bytes_consumed:])
                return bytes_consumed
            item = Item()
            bytes_consumed += item.parse_content(data[bytes_consumed:])
            self.data.append(item)
            peek = data[bytes_consumed : bytes_consumed + 1]
            if not peek:
                raise ValueError("End of inner list not found")
            if peek not in b" )":
                raise ValueError("Inner list bad delimitation")

    def __str__(self) -> str:
        output = "("
        count = len(self.data)
        for x in range(0, count):
            output += str(self[x])
            if x + 1 < count:
                output += " "
        output += ")"
        output += str(self.params)
        return output

    def __setitem__(
        self,
        index: Union[int, slice],
        value: Union[SingleItemType, Iterable[SingleItemType]],
    ) -> None:
        if isinstance(index, slice):
            self.data[index] = [itemise(v) for v in value]  # type: ignore
        else:
            self.data[index] = itemise(cast(SingleItemType, value))

    def append(self, item: SingleItemType) -> None:
        self.data.append(itemise(item))

    def insert(self, i: int, item: SingleItemType) -> None:
        self.data.insert(i, itemise(item))

    def to_json(self) -> JsonType:
        return [[i.to_json() for i in self.data], self.params.to_json()]

    def from_json(self, json_data: JsonType) -> None:
        try:
            values, params = json_data
        except ValueError:
            raise ValueError(json_data)
        for i in values:
            self.data.append(Item())
            self[-1].from_json(i)
        self.params.from_json(params)


_parse_map = {
    DQUOTE: parse_string,
    BYTE_DELIMIT: parse_byteseq,
    ord(b"?"): parse_boolean,
}
for c in TOKEN_START_CHARS:
    _parse_map[c] = parse_token
for c in NUMBER_START_CHARS:
    _parse_map[c] = parse_number


def parse_bare_item(data: bytes) -> Tuple[int, BareItemType]:
    if not data:
        raise ValueError("Empty item")
    try:
        return _parse_map[data[0]](data)  # type: ignore
    except KeyError:
        raise ValueError(
            f"Item starting with '{data[0:1].decode('ascii')}' can't be identified"
        )


def ser_bare_item(item: BareItemType) -> str:
    item_type = type(item)
    if item_type is int:
        return ser_integer(cast(int, item))
    if isinstance(item, (Decimal, float)):
        return ser_decimal(item)
    if isinstance(item, Token):
        return ser_token(item)
    if item_type is str:
        return ser_string(cast(str, item))
    if item_type is bool:
        return ser_boolean(cast(bool, item))
    if item_type is bytes:
        return ser_byteseq(cast(bytes, item))
    raise ValueError(f"Can't serialise; unrecognised item with type {item_type}")


def itemise(thing: Union[BareItemType, InnerList, Item]) -> Union[InnerList, Item]:
    if isinstance(thing, (Item, InnerList)):
        return thing
    if isinstance(thing, list):
        return InnerList(thing)
    return Item(thing)


AllItemType = Union[BareItemType, Item, InnerList]
