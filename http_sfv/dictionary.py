from typing import Tuple

from .item import ser_item, bin_ser_item, parse_params, ser_params
from .list import parse_item_or_inner_list, bin_parse_item_or_inner_list
from .types import DictionaryType
from .util import (
    discard_http_ows,
    ser_key,
    parse_key,
)
from .util_binary import decode_integer, encode_integer, bin_header, STYPE


EQUALS = ord(b"=")
COMMA = ord(b",")


def parse_dictionary(data: bytes) -> Tuple[int, DictionaryType]:
    bytes_consumed = 0
    dictionary = {}
    data_len = len(data)
    try:
        while True:
            offset, this_key = parse_key(data[bytes_consumed:])
            bytes_consumed += offset
            try:
                is_equals = data[bytes_consumed] == EQUALS
            except IndexError:
                is_equals = False
            if is_equals:
                bytes_consumed += 1  # consume the "="
                offset, member = parse_item_or_inner_list(data[bytes_consumed:])
                bytes_consumed += offset
            else:
                params_consumed, params = parse_params(data[bytes_consumed:])
                bytes_consumed += params_consumed
                member = (True, params)
            dictionary[this_key] = member
            bytes_consumed += discard_http_ows(data[bytes_consumed:])
            if bytes_consumed == data_len:
                return bytes_consumed, dictionary
            if data[bytes_consumed] != COMMA:
                raise ValueError(
                    f"Dictionary member '{this_key}' has trailing characters"
                )
            bytes_consumed += 1
            bytes_consumed += discard_http_ows(data[bytes_consumed:])
            if bytes_consumed == data_len:
                raise ValueError("Dictionary has trailing comma")
    except Exception as why:
        raise ValueError from why


def bin_parse_dictionary(data: bytearray) -> Tuple[int, DictionaryType]:
    cursor = 1  # header
    dictionary = {}
    bytes_consumed, member_count = decode_integer(data[cursor:])
    cursor += bytes_consumed
    for _ in range(member_count):
        key_len = data[cursor]
        cursor += 1
        key_end = cursor + key_len
        key = data[cursor:key_end].decode("ascii")
        cursor = key_end
        bytes_consumed, value = bin_parse_item_or_inner_list(data[cursor:])
        cursor += bytes_consumed
        dictionary[key] = value
    return cursor, dictionary


def ser_dictionary(dictionary: DictionaryType) -> str:
    if len(dictionary) == 0:
        raise ValueError("No contents; field should not be emitted")
    return ", ".join(
        [
            f"{ser_key(m)}"
            f"""{ser_params(n[1]) if
                (isinstance(n, tuple) and n[0] is True)
                else f'={ser_item(n)}'}"""  # type: ignore
            for m, n in dictionary.items()
        ]
    )


def bin_ser_dictionary(dictionary: DictionaryType) -> bytearray:
    data = bin_header(STYPE.DICTIONARY)
    data += encode_integer(len(dictionary))
    for member in dictionary:
        data.append(len(member))  # fixme: catch too many
        data += member.encode("ascii")
        data += bin_ser_item(dictionary[member])  # type: ignore
    return data
