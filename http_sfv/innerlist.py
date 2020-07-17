from typing import Any

from .item import Item, Parameters
from .util import remove_char, discard_ows


class InnerList(list):
    def __init__(self, values: list = None) -> None:
        list.__init__(self, values or [])
        self.params = Parameters()

    def parse(self, input_string: str) -> str:
        input_string, char = remove_char(input_string)
        if char != "(":
            raise ValueError(
                f"First character of inner list is not '(' at: {input_string[:10]}"
            )
        while input_string:
            input_string = discard_ows(input_string)
            if input_string and input_string[0] == ")":
                input_string = input_string[1:]
                return self.params.parse(input_string)
            item = Item()
            input_string = item.parse_content(input_string)
            self.append(item)
            if not (input_string and input_string[0] in set(" )")):
                raise ValueError(f"Inner list bad delimitation at: {input_string[:10]}")
        raise ValueError(f"End of inner list not found at: {input_string[:10]}")

    def __str__(self) -> str:
        output = "("
        count = len(self)
        for x in range(0, count):
            output += str(self[x])
            if x + 1 < count:
                output += " "
        output += ")"
        output += str(self.params)
        return output

    def to_json(self) -> Any:
        return [[i.to_json() for i in self], self.params.to_json()]

    def from_json(self, json_data: Any) -> None:
        try:
            values, params = json_data
        except ValueError:
            raise ValueError(json_data)
        for i in values:
            self.append(Item())
            self[-1].from_json(i)
        self.params.from_json(params)
