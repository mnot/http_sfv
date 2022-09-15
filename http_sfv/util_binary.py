from enum import IntEnum
from typing import Tuple, Union


HEADER_BITS = 5


class TLTYPE(IntEnum):
    RAW = 0
    DICTIONARY = 1
    LIST = 2
    ITEM = 3


class STYPE(IntEnum):
    INNER_LIST = 1
    PARAMETER = 2
    INTEGER = 3
    DECIMAL = 4
    STRING = 5
    TOKEN = 6
    BYTESEQ = 7
    BOOLEAN = 8


def bin_header(
    sf_type: Union[TLTYPE, STYPE],
    parameters: bool = False,
    flag1: bool = False,
    flag2: bool = False,
) -> bytearray:
    data = bytearray([0])
    data[0] |= sf_type << HEADER_BITS
    return data


def decode_integer(data: bytearray) -> Tuple[int, int]:
    val = data[0]
    prefix = val >> 6
    length = 1 << prefix
    val = val & 0x3F
    for i in range(1, length):
        val = (val << 8) + data[i]
    return length, val


UINT8 = 256


def encode_integer(i: int) -> bytearray:
    if i <= 63:
        return bytearray([i])
    if i <= 16383:
        return bytearray([i >> 8 | 0x40, i % UINT8])
    if i <= 1073741823:
        return bytearray(
            [i >> 24 | 0x80, (i >> 16) % UINT8, (i >> 8) % UINT8, i % UINT8]
        )
    if i <= 4611686018427387903:
        return bytearray(
            [
                (i >> 56) % UINT8 | 0xC0,
                (i >> 48) % UINT8,
                (i >> 40) % UINT8,
                (i >> 32) % UINT8,
                (i >> 24) % UINT8,
                (i >> 16) % UINT8,
                (i >> 8) % UINT8,
                i % UINT8,
            ]
        )
    raise ValueError(f"{i} doesn't fit into 62 bits")
