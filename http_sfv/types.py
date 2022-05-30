from collections import UserString
from decimal import Decimal
from typing import Union, Dict, List, Tuple


class Token(UserString):
    pass


BareItemType = Union[int, float, str, bool, Decimal, bytes, Token]
JsonBareType = Union[int, float, str, bool, Decimal, Dict]

JsonParamType = List[Tuple[str, JsonBareType]]
JsonItemType = Tuple[JsonBareType, JsonParamType]
JsonInnerListType = Tuple[List[JsonItemType], JsonParamType]
JsonListType = List[Union[JsonItemType, JsonInnerListType]]
JsonDictType = List[Tuple[str, Union[JsonItemType, JsonInnerListType]]]
