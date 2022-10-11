#!/usr/bin/env python

"Structured HTTP Field Values"

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

__version__ = "0.9.8"

from typing import Tuple, List, Dict

from .dictionary import (
    parse_dictionary,
    bin_parse_dictionary,
    ser_dictionary,
    bin_ser_dictionary,
)
from .item import parse_item, bin_parse_item, ser_item, bin_ser_item
from .list import parse_list, bin_parse_list, ser_list, bin_ser_list
from .retrofit import retrofit
from .types import StructuredType, Token
from .util import discard_ows
from .util_binary import HEADER_OFFSET, STYPE


def parse_text(
    value: bytes, name: str = None, tltype: str = None
) -> Tuple[int, StructuredType]:
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
    return bytes_consumed, structure


def parse_binary(data: bytes) -> Tuple[int, StructuredType]:
    tltype = data[0] >> HEADER_OFFSET
    if tltype == STYPE.DICTIONARY:
        return bin_parse_dictionary(data, 0)
    if tltype == STYPE.LIST:
        return bin_parse_list(data, 0)
    return bin_parse_item(data, 0)


def ser_text(structure: StructuredType) -> str:
    if isinstance(structure, Dict):
        return ser_dictionary(structure)
    if isinstance(structure, List):
        return ser_list(structure)
    return ser_item(structure)


def ser_binary(structure: StructuredType) -> bytes:
    if isinstance(structure, Dict):
        return bin_ser_dictionary(structure)
    if isinstance(structure, List):
        return bin_ser_list(structure)
    return bin_ser_item(structure)
