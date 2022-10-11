from decimal import Decimal
from typing import Tuple, Union, cast

from http_sfv.integer import parse_number
from http_sfv.util_binary import (
    decode_integer,
    encode_integer,
    bin_header,
    extract_flags,
    STYPE,
)


INT_DIGITS = 12
FRAC_DIGITS = 3
PRECISION = Decimal(10) ** -FRAC_DIGITS


def parse_decimal(data: bytes) -> Tuple[int, Decimal]:
    return cast(Tuple[int, Decimal], parse_number(data))


def ser_decimal(input_decimal: Union[Decimal, float]) -> str:
    if isinstance(input_decimal, float):
        input_decimal = Decimal(input_decimal)
    if not isinstance(input_decimal, Decimal):
        raise ValueError("decimal input is not decimal")
    input_decimal = round(input_decimal, FRAC_DIGITS)
    abs_decimal = input_decimal.copy_abs()
    integer_component_s = str(int(abs_decimal))
    if len(integer_component_s) > INT_DIGITS:
        raise ValueError(
            f"decimal with oversize integer component {integer_component_s}"
        )
    fractional_component = abs_decimal.quantize(PRECISION).normalize() % 1
    return (
        f"{'-' if input_decimal < 0 else ''}{integer_component_s}."
        f"{str(fractional_component)[2:] if fractional_component else '0'}"
    )


def bin_parse_decimal(data: bytes, cursor: int) -> Tuple[int, Decimal]:
    cursor, int_a = decode_integer(data, cursor + 1)  # +1 for header
    cursor, int_b = decode_integer(data, cursor)
    if extract_flags(data[cursor])[0]:
        return cursor, Decimal(int_a) / int_b
    return cursor, (Decimal(int_a) / int_b) * -1


def bin_ser_decimal(value: Decimal, parameters: bool) -> bytes:
    int_a, int_b = value.as_integer_ratio()
    sign = int_a >= 0
    data = [bin_header(STYPE.DECIMAL, parameters=parameters, flag1=sign)]
    data.append(encode_integer(abs(int_a)))
    data.append(encode_integer(int_b))
    return b"".join(data)
