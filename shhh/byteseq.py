import base64
from string import ascii_letters, digits
from typing import Tuple

BYTE_DELIMIT = ":"
B64CONTENT = set(ascii_letters + digits + "+/=")


def parse_byteseq(input_string: str) -> Tuple[str, bytes]:
    if input_string and input_string[0] is not BYTE_DELIMIT:
        raise ValueError(
            f"Binary Sequence didn't start with '{BYTE_DELIMIT}' at: {input_string[:10]}"
        )
    input_string = input_string[1:]
    if BYTE_DELIMIT not in input_string:
        raise ValueError(
            f"Binary Sequence didn't contain ending '{BYTE_DELIMIT}' at: {input_string[:10]}"
        )
    b64_content = input_string[: input_string.index(BYTE_DELIMIT)]
    input_string = input_string[input_string.index(BYTE_DELIMIT) + 1 :]
    if not all(c in B64CONTENT for c in b64_content):
        raise ValueError(
            f"Binary Sequence contained disallowed character at: {input_string[:10]}"
        )
    binary_content = base64.standard_b64decode(b64_content)
    return input_string, binary_content


def ser_byteseq(byteseq: bytes) -> str:
    output = ""
    output += BYTE_DELIMIT
    output += base64.standard_b64encode(byteseq).decode("ascii")
    output += BYTE_DELIMIT
    return output
