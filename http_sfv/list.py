from typing import Tuple, Any

from .innerlist import InnerList
from .item import Item
from .util import StructuredFieldValue, discard_http_ows, remove_char


class List(list, StructuredFieldValue):
    def parse_content(self, input_string: str) -> str:
        while input_string:
            input_string, member = parse_item_or_inner_list(input_string)
            self.append(member)
            input_string = discard_http_ows(input_string)
            if not input_string:
                return input_string
            input_string, char = remove_char(input_string)
            if char != ",":
                raise ValueError(
                    f"Trailing text after item in list at: {input_string[:10]}"
                )
            input_string = discard_http_ows(input_string)
            if not input_string:
                raise ValueError(
                    f"Trailing comma at end of list at: {input_string[:10]}"
                )
        return input_string

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

    def to_json(self) -> Any:
        return [i.to_json() for i in self]

    def from_json(self, json_data: Any) -> None:
        for i in json_data:
            if isinstance(i[0], list):
                self.append(InnerList())
            else:
                self.append(Item())
            self[-1].from_json(i)


def parse_item_or_inner_list(input_string: str) -> Tuple[str, Any]:
    if input_string and input_string[0] == "(":
        inner_list = InnerList()
        input_string = inner_list.parse(input_string)
        return input_string, inner_list
    item = Item()
    input_string = item.parse_content(input_string)
    return input_string, item
