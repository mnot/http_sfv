from typing import Any

from .item import Item, Parameters, ser_key, parse_key
from .list import InnerList, parse_item_or_inner_list
from .util import StructuredFieldValue, remove_char, discard_http_ows


class Dictionary(dict, StructuredFieldValue):
    def parse_content(self, input_string: str) -> str:
        while input_string:
            input_string, this_key = parse_key(input_string)
            if input_string and input_string[0] == "=":
                input_string, char = remove_char(input_string)
                input_string, member = parse_item_or_inner_list(input_string)
            else:
                member = Item()
                member.value = True
                member.params = Parameters()
                input_string = member.params.parse(input_string)
            self[this_key] = member
            input_string = discard_http_ows(input_string)
            if not input_string:
                return input_string
            input_string, char = remove_char(input_string)
            if char != ",":
                raise ValueError(
                    f"Dictionary member trailing characters at: {input_string[:10]}"
                )
            input_string = discard_http_ows(input_string)
            if not input_string:
                raise ValueError(
                    f"Dictionary has trailing comma at: {input_string[:10]}"
                )
        return input_string

    def __str__(self) -> str:
        output = ""
        count = len(self)
        i = 0
        for member_name in self.keys():
            i += 1
            output += ser_key(member_name)
            if isinstance(self[member_name], Item) and self[member_name].value is True:
                output += str(self[member_name].params)
            else:
                output += "="
                output += str(self[member_name])
            if i < count:
                output += ", "
        return output

    def to_json(self) -> Any:
        return {k: v.to_json() for (k, v) in self.items()}

    def from_json(self, json_data: Any) -> None:
        for k, v in json_data.items():
            if isinstance(v[0], list):
                self[k] = InnerList()
            else:
                self[k] = Item()
            self[k].from_json(v)
