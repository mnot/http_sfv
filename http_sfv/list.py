from collections import UserList
from typing import Tuple, Union, Iterable, cast

from .item import Item, InnerList, itemise, AllItemType
from .types import JsonType
from .util import StructuredFieldValue, discard_http_ows, remove_char, next_char


class List(UserList, StructuredFieldValue):
    def parse_content(self, data: bytes) -> int:
        bytes_consumed = 0
        while True:
            offset, member = parse_item_or_inner_list(data[bytes_consumed:])
            bytes_consumed += offset
            self.append(member)
            bytes_consumed += discard_http_ows(data[bytes_consumed:])
            if not data[bytes_consumed:]:
                return bytes_consumed
            offset, char = remove_char(data[bytes_consumed:])
            bytes_consumed += offset
            if char != b",":
                raise ValueError("Trailing text after item in list")
            bytes_consumed += discard_http_ows(data[bytes_consumed:])
            if not data[bytes_consumed:]:
                raise ValueError("Trailing comma at end of list")

    def __str__(self) -> str:
        if len(self) == 0:
            raise ValueError("No contents; field should not be emitted")
        output = ""
        count = len(self)
        for x in range(0, count):
            output += str(self[x])
            if x + 1 < count:
                output += ", "
        return output

    def __setitem__(
        self, index: Union[int, slice], value: Union[AllItemType, Iterable[AllItemType]]
    ) -> None:
        if isinstance(index, slice):
            self.data[index] = [itemise(v) for v in value]  # type: ignore
        else:
            self.data[index] = itemise(cast(AllItemType, value))

    def append(self, item: AllItemType) -> None:
        self.data.append(itemise(item))

    def insert(self, i: int, item: AllItemType) -> None:
        self.data.insert(i, itemise(item))

    def to_json(self) -> JsonType:
        return [i.to_json() for i in self]

    def from_json(self, json_data: JsonType) -> None:
        for i in json_data:
            if isinstance(i[0], list):
                self.append(InnerList())
            else:
                self.append(Item())
            self[-1].from_json(i)


def parse_item_or_inner_list(data: bytes) -> Tuple[int, Union[Item, InnerList]]:
    if next_char(data) == b"(":
        inner_list = InnerList()
        bytes_consumed = inner_list.parse(data)
        return bytes_consumed, inner_list
    item = Item()
    bytes_consumed = item.parse_content(data)
    return bytes_consumed, item
