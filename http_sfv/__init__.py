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

__version__ = "0.8.2"

from typing import Any

from .util import discard_ows
from .dictionary import parse_dictionary, ser_dictionary
from .list import parse_list, ser_list
from .item import parse_item, ser_item


def parse(input_string: str, field_type: str) -> Any:
    input_string = discard_ows(input_string)
    if field_type == "list":
        input_string, output = parse_list(input_string)  # type: ignore
    elif field_type == "dictionary":
        input_string, output = parse_dictionary(input_string)  # type: ignore
    elif field_type == "item":
        input_string, output = parse_item(input_string)  # type: ignore
    else:
        raise ValueError(f"Unrecognised field type '{field_type}'")
    input_string = discard_ows(input_string)
    if input_string:
        raise ValueError(f"Trailing text after parsed value at: {input_string[:10]}")
    return output


def serialise(input_data: Any, field_type: str) -> str:
    if field_type in ["list", "dictionary"]:
        if not input_data:
            return None  # Do not serialise this header
    if field_type == "dictionary":
        return ser_dictionary(input_data)
    if field_type == "list":
        return ser_list(input_data)
    if field_type == "item":
        return ser_item(input_data[0], input_data[1])
    raise ValueError(f"Unrecognised field_type {field_type}")
