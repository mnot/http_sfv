#!/usr/bin/env python

"Structured HTTP Headers"

__author__ = "Mark Nottingham <mnot@mnot.net>"
__copyright__ = """\
Copyright (c) 2018 Mark Nottingham

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

__version__ = "0.1.0"

from typing import Any

from .util import discard_ows
from .dictionary import parse_dictionary, ser_dictionary
from .list import parse_list, ser_list
from .item import parse_item, ser_item

def parse(input_string: str, header_type: str) -> Any:
    input_string = discard_ows(input_string)
    if header_type == "dictionary":
        input_string, output = parse_dictionary(input_string) # type: ignore
    if header_type == "list":
        input_string, output = parse_list(input_string)  # type: ignore
    if header_type == "item":
        input_string, output = parse_item(input_string)  # type: ignore
    input_string = discard_ows(input_string)
    if input_string:
        raise ValueError("Trailing text after parsed value.", input_string)
    return output

def serialise(input_data: Any) -> str:
    data_type = type(input_data)
    if data_type == dict:
        return ser_dictionary(input_data)
    if data_type == list:
        return ser_list(input_data)
    if data_type in [str, int, float, bool, bytes]:
        return ser_item(input_data)
    raise ValueError("Unrecognised input data.")
