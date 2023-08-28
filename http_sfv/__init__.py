#!/usr/bin/env python

"Structured HTTP Field Values"

__author__ = "Mark Nottingham <mnot@mnot.net>"
__copyright__ = """\
Copyright (c) Mark Nottingham

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

__version__ = "0.9.8"

from typing import Tuple, List, Dict

from http_sfv.dictionary import parse_dictionary, ser_dictionary
from http_sfv.item import parse_item, ser_item
from http_sfv.list import parse_list, ser_list
from http_sfv.retrofit import retrofit
from http_sfv.types import StructuredType, Token
from http_sfv.util import discard_ows


def parse_text(value: bytes, name: str = None, tltype: str = None) -> StructuredType:
    structure: StructuredType
    if name is not None:
        tltype = retrofit.get(name.lower(), None)
    cursor = discard_ows(value)
    if tltype == "dictionary":
        bytes_consumed, structure = parse_dictionary(value[cursor:])
    elif tltype == "list":
        bytes_consumed, structure = parse_list(value[cursor:])
    elif tltype == "item":
        bytes_consumed, structure = parse_item(value[cursor:])
    else:
        raise KeyError("unrecognised top-level type")
    cursor += bytes_consumed
    if discard_ows(value[cursor:]) < len(value) - cursor:
        raise ValueError("Trailing characters after value.")
    return structure


def ser_text(structure: StructuredType) -> str:
    if isinstance(structure, Dict):
        return ser_dictionary(structure)
    if isinstance(structure, List):
        return ser_list(structure)
    return ser_item(structure)
