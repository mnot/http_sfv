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

from typing import Tuple

from .dictionary import Dictionary
from .list import List
from .item import Item, InnerList
from .token import Token
from .util import StructuredFieldValue
from .util_binary import HEADER_BITS, STYPE

structures = {"dictionary": Dictionary, "list": List, "item": Item}


def parse_binary(data: bytes) -> Tuple[int, StructuredFieldValue]:
    stype = data[0] >> HEADER_BITS
    if stype == STYPE.DICTIONARY:
        top_level = Dictionary()
    elif stype == STYPE.LIST:
        top_level = List()
    else:
        top_level = Item()
    bytes_consumed = top_level.from_binary(data)
    return bytes_consumed, top_level
