import base64
from string import ascii_letters, digits
from typing import Tuple

from .util import next_char

BYTE_DELIMIT = b":"
B64CONTENT = (ascii_letters + digits + "+/=").encode("ascii")


def parse_byteseq(data: bytes) -> Tuple[int, bytes]:
    if next_char(data) != BYTE_DELIMIT:
        raise ValueError("Binary Sequence didn't start with ':'")
    bytes_consumed = 1
    try:
        end_delimit = data[bytes_consumed:].index(BYTE_DELIMIT)
    except ValueError:
        raise ValueError("Binary Sequence didn't contain ending ':'")
    b64_content = data[bytes_consumed : bytes_consumed + end_delimit]
    bytes_consumed += end_delimit
    if not all(c in B64CONTENT for c in b64_content):
        raise ValueError("Binary Sequence contained disallowed character")
    binary_content = base64.standard_b64decode(b64_content)
    return bytes_consumed, binary_content


def ser_byteseq(byteseq: bytes) -> str:
    output = ""
    output += ":"
    output += base64.standard_b64encode(byteseq).decode("ascii")
    output += ":"
    return output
