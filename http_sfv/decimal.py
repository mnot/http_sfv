from decimal import Decimal
from typing import Tuple, Union

from .integer import parse_number
from .util_binary import decode_integer, encode_integer, bin_header, STYPE


INT_DIGITS = 12
FRAC_DIGITS = 3
PRECISION = Decimal(10) ** -FRAC_DIGITS


def parse_decimal(data: bytes) -> Tuple[int, Decimal]:
    return parse_number(data)  # type: ignore


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


def bin_parse_decimal(data: bytearray) -> Tuple[int, Decimal]:
    """
    Payload: Integer i, Integer f - indicating the integer and fractional components in use
    """
    ## TODO: sign
    header = data.pop(0)
    bytes_consumed, integer_component = decode_integer(data)
    bytes_consumed += 1  # header
    offset, fractional_component = decode_integer(data[bytes_consumed:])
    return bytes_consumed + offset, Decimal()  # FIXME


def bin_ser_decimal(value: Decimal) -> bytearray:
    ## TODO: sign
    input_decimal = round(value, FRAC_DIGITS)
    abs_decimal = value.copy_abs()
    integer_component = int(abs_decimal)
    fractional_component = int(str(abs_decimal.quantize(PRECISION).normalize() % 1)[2:])
    data = bin_header(STYPE.DECIMAL)
    data += encode_integer(integer_component)
    data += encode_integer(fractional_component)
    return data
