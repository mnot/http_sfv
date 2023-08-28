from typing import Tuple

from http_sfv.item import ser_item
from http_sfv.innerlist import parse_item_or_inner_list
from http_sfv.parameters import parse_params, ser_params
from http_sfv.types import DictionaryType
from http_sfv.util import discard_http_ows, ser_key, parse_key


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
