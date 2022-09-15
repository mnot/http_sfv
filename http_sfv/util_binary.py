from enum import IntEnum
from typing import Tuple


__doc__ = """
Each structure has a one-byte header, whose bits are:

|ttttxxxx|

- The first four `t` bits indicate the type of the structure. Each type has a specific payload
- The last four `x` bits are available for the structure's use
Each structure is self-delimiting.
"""

# FIXME: value content validation

HEADER_BITS = 4
HEADER_MASK = 0b00001111


class STYPE(IntEnum):
    DICTIONARY = 1
    LIST = 2
    INNER_LIST = 3
    INTEGER = 4
    DECIMAL = 5
    BOOLEAN = 6
    BYTESEQ = 7
    STRING = 8
    TOKEN = 9


def add_type(data: bytearray, sf_type: STYPE) -> bytearray:
    data[0] = (sf_type << HEADER_BITS) | data[0]
    return data


#### From hyper hpack

# Precompute 2^i for 1-8 for use in prefix calcs.
# Zero index is not used but there to save a subtraction
# as prefix numbers are not zero indexed.
_PREFIX_BIT_MAX_NUMBERS = [(2**i) - 1 for i in range(9)]


def decode_integer(prefix_bits: int, data: bytes) -> Tuple[int, int]:
    """
    This decodes an integer according to the wacky integer encoding rules
    defined in the HPACK spec. Returns a tuple of the decoded integer and the
    number of bytes that were consumed from ``data`` in order to get that
    integer.
    """
    if prefix_bits < 1 or prefix_bits > 8:
        raise ValueError(f"Prefix bits must be between 1 and 8, got {prefix_bits}")

    max_number = _PREFIX_BIT_MAX_NUMBERS[prefix_bits]
    index = 1
    shift = 0
    mask = 0xFF >> (8 - prefix_bits)

    try:
        number = data[0] & mask
        if number == max_number:
            while True:
                next_byte = data[index]
                index += 1

                if next_byte >= 128:
                    number += (next_byte - 128) << shift
                else:
                    number += next_byte << shift
                    break
                shift += 7

    except IndexError:
        raise ValueError("Unable to decode HPACK integer representation from %r" % data)

    return index, number


def encode_integer(integer: int, prefix_bits: int) -> bytearray:
    """
    This encodes an integer according to the wacky integer encoding rules
    defined in the HPACK spec.
    """

    if integer < 0:
        raise ValueError(f"Can only encode positive integers, got {integer}")

    if prefix_bits < 1 or prefix_bits > 8:
        raise ValueError(f"Prefix bits must be between 1 and 8, got {prefix_bits}")

    max_number = _PREFIX_BIT_MAX_NUMBERS[prefix_bits]

    if integer < max_number:
        return bytearray([integer])  # Seriously?
    elements = [max_number]
    integer -= max_number

    while integer >= 128:
        elements.append((integer & 127) + 128)
        integer >>= 7

    elements.append(integer)

    return bytearray(elements)
