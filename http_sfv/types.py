from collections import UserString
from decimal import Decimal
from typing import Union, Any


class Token(UserString):
    pass


BareItemType = Union[int, float, str, bool, bytes, Decimal, Token]

JsonType = Any
