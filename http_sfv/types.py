from collections import UserString
from decimal import Decimal
from typing import Union, Dict, List, Tuple


class Token(UserString):
    def __init__(self, seq: str):
        self.data = seq

    def __repr__(self):
        return f'Token("{self.data}")'


BareItemType = Union[int, float, str, bool, Decimal, bytes, Token]
ParamsType = Dict[str, BareItemType]
ItemType = Tuple[BareItemType, ParamsType]
InnerListType = Tuple[List[ItemType], ParamsType]
ItemOrInnerListType = Union[ItemType, InnerListType]
ListType = List[Union[ItemType, InnerListType]]
DictionaryType = Dict[str, Union[ItemType, InnerListType]]
StructuredType = Union[ItemType, ListType, DictionaryType]
