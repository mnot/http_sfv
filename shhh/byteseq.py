
import base64
from string import ascii_letters, digits
from typing import Tuple

def parse_byteseq(input_string: str) -> Tuple[str, bytes]:
    if input_string and input_string[0] != "*":
        raise ValueError("Binary Sequence didn't start with '*'.", input_string)
    input_string = input_string[1:]
    if "*" not in input_string:
        raise ValueError("Binary Sequence didn't contain ending '*'.", input_string)
    b64_content = input_string[:input_string.index("*")]
    input_string = input_string[input_string.index("*") + 1:]
    if not all(c in ascii_letters + digits + '+/=' for c in b64_content):
        raise ValueError("Binary Sequence contained disallowed character.", input_string)
    binary_content = base64.standard_b64decode(b64_content)
    return input_string, binary_content

def ser_byteseq(byteseq: bytes) -> str:
    if type(byteseq) is not bytes:
        raise ValueError("Input is not bytes.")
    output = ""
    output += "*"
    output += base64.standard_b64encode(byteseq).decode('ascii')
    output += "*"
    return output
