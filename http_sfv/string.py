from typing import Tuple

DQUOTE = b'"'
BACKSLASH = b"\\"
DQUOTEBACKSLASH = DQUOTE + BACKSLASH


def parse_string(data: bytes) -> Tuple[int, str]:
    output_string = []
    if not data or data[0:1] != DQUOTE:
        raise ValueError("First character of string is not DQUOTE")
    bytes_consumed = 1
    while True:
        char = data[bytes_consumed : bytes_consumed + 1]
        bytes_consumed += 1
        if not char:
            raise ValueError("Reached end of input without finding a closing DQUOTE")
        if char == BACKSLASH:
            if not data[bytes_consumed:]:
                raise ValueError("Last character of input was a backslash")
            next_char = data[bytes_consumed : bytes_consumed + 1]
            bytes_consumed += 1
            if not next_char or next_char not in DQUOTEBACKSLASH:
                raise ValueError(
                    f"Backslash before disallowed character '{next_char.decode('ascii')}'"
                )
            output_string.append(next_char)
        elif char == DQUOTE:
            return bytes_consumed, (b"".join(output_string)).decode("ascii")
        elif not 31 < char[0] < 127:
            raise ValueError("String contains disallowed character")
        else:
            output_string.append(char)


def ser_string(inval: str) -> str:
    if not all(31 < ord(char) < 127 for char in inval):
        raise ValueError("String contains disallowed characters")
    output = ""
    output += '"'
    for char in inval:
        if char in '"\\':
            output += "\\"
        output += char
    output += '"'
    return output
