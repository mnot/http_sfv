#!/usr/bin/env python

"Structured HTTP Headers"

__author__ = "Mark Nottingham <mnot@mnot.net>"
__copyright__ = """\
Copyright (c) 2018-2020 Mark Nottingham

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

__version__ = "0.8.3"

from typing import Any

from .util import discard_ows
from .dictionary import Dictionary
from .list import List
from .item import Item


class StructuredFieldValue:
    def __init__(self, field_type: str) -> None:
        self.field_type = field_type
        if self.field_type == "list":
            self.value = List()  # type: ignore
        elif self.field_type == "dictionary":
            self.value = Dictionary()  # type: ignore
        elif self.field_type == "item":
            self.value = Item()  # type: ignore
        else:
            raise ValueError(f"Unrecognised field type '{self.field_type}'")
        self.raw_value = None  # type: str

    def parse(self, input_string: str) -> None:
        self.raw_value = input_string
        input_string = discard_ows(input_string)

        input_string = self.value.parse(input_string)  # type: ignore
        input_string = discard_ows(input_string)
        if input_string:
            raise ValueError(
                f"Trailing text after parsed value at: {input_string[:10]}"
            )

    def __str__(self) -> str:
        if self.field_type in ["list", "dictionary"]:
            if not self.value:
                return ""  # Do not serialise this header
        return str(self.value)

    def to_json(self) -> Any:
        return self.value.to_json()  # type: ignore

    def from_json(self, json_data: Any) -> None:
        self.value.from_json(json_data)  # type: ignore
