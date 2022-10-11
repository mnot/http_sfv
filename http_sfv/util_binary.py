from enum import IntEnum
from typing import Tuple


HEADER_OFFSET = 3


class STYPE(IntEnum):
    LITERAL = 0
    LIST = 1
    DICTIONARY = 2
    INNER_LIST = 3
    PARAMETER = 4
    INTEGER = 5
    DECIMAL = 6
    STRING = 7
    TOKEN = 8
    BYTESEQ = 9
    BOOLEAN = 10


def bin_header(
    sf_type: STYPE,
    parameters: bool = False,
    flag1: bool = False,
    flag2: bool = False,
) -> bytes:
    data = bytearray([0])
    data[0] |= sf_type << HEADER_OFFSET
    if parameters:
        data[0] |= 1 << 2
    if flag1:
        data[0] |= 1 << 1
    if flag2:
        data[0] |= 1 << 0
    return bytes(data)


def extract_flags(header: int) -> Tuple[bool, bool]:
    return ((header & 0b00000010) > 0, (header & 0b00000001) > 0)


def has_params(header: int) -> bool:
    return (header & 0b00000100) > 0


def decode_integer(data: bytes, cursor: int) -> Tuple[int, int]:
    val = data[cursor]
    end = cursor + (1 << (val >> 6))
    val = val & 0x3F
    for i in range(cursor + 1, end):
        val = (val << 8) + data[i]
    return end, val


UINT8 = 256


def encode_integer(i: int) -> bytes:
    if i <= 63:
        return bytes([i])
    if i <= 16383:
        return bytes([i >> 8 | 0x40, i % UINT8])
    if i <= 1073741823:
        return bytes([i >> 24 | 0x80, (i >> 16) % UINT8, (i >> 8) % UINT8, i % UINT8])
    if i <= 4611686018427387903:
        return bytes(
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
