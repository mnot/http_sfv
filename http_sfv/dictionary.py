from collections import UserDict

from .item import Item, InnerList, itemise, AllItemType
from .list import parse_item_or_inner_list
from .types import JsonType
from .util import (
    StructuredFieldValue,
    discard_http_ows,
    ser_key,
    parse_key,
)

EQUALS = ord(b"=")
COMMA = ord(b",")


class Dictionary(UserDict, StructuredFieldValue):
    def parse_content(self, data: bytes) -> int:
        bytes_consumed = 0
        data_len = len(data)
        while True:
            offset, this_key = parse_key(data[bytes_consumed:])
            bytes_consumed += offset
            try:
                is_equals = data[bytes_consumed] == EQUALS
            except IndexError:
                is_equals = False
            if is_equals:
                bytes_consumed += 1  # consume the "="
                offset, member = parse_item_or_inner_list(data[bytes_consumed:])
                bytes_consumed += offset
            else:
                member = Item()
                member.value = True
                bytes_consumed += member.params.parse(data[bytes_consumed:])
            self[this_key] = member
            bytes_consumed += discard_http_ows(data[bytes_consumed:])
            if bytes_consumed == data_len:
                return bytes_consumed
            if data[bytes_consumed] != COMMA:
                raise ValueError("Dictionary member has trailing characters")
            bytes_consumed += 1
            bytes_consumed += discard_http_ows(data[bytes_consumed:])
            if bytes_consumed == data_len:
                raise ValueError("Dictionary has trailing comma")

    def __setitem__(self, key: str, value: AllItemType) -> None:
        self.data[key] = itemise(value)

    def __str__(self) -> str:
        if len(self) == 0:
            raise ValueError("No contents; field should not be emitted")
        return ", ".join(
            [
                f"{ser_key(m)}"
                f"""{self[m].params if
                    (isinstance(self[m], Item) and self[m].value is True)
                    else f'={self[m]}'}"""
                for m in self.keys()
            ]
        )

    def to_json(self) -> JsonType:
        return {k: v.to_json() for (k, v) in self.items()}

    def from_json(self, json_data: JsonType) -> None:
        for k, v in json_data.items():
            if isinstance(v[0], list):
                self[k] = InnerList()
            else:
                self[k] = Item()
            self[k].from_json(v)
