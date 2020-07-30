from typing import Tuple

DQUOTE = ord('"')
BACKSLASH = ord("\\")
DQUOTEBACKSLASH = set([DQUOTE, BACKSLASH])


def parse_string(data: bytes) -> Tuple[int, str]:
    output_string = bytearray()
    if data[0] != DQUOTE:
        raise ValueError("First character of string is not DQUOTE")
    bytes_consumed = 1
    while True:
        try:
            char = data[bytes_consumed]
        except IndexError:
            raise ValueError("Reached end of input without finding a closing DQUOTE")
        bytes_consumed += 1
        if char == BACKSLASH:
            try:
                next_char = data[bytes_consumed]
            except IndexError:
                raise ValueError("Last character of input was a backslash")
            bytes_consumed += 1
            if next_char not in DQUOTEBACKSLASH:
                raise ValueError(
                    f"Backslash before disallowed character '{chr(next_char)}'"
                )
            output_string.append(next_char)
        elif char == DQUOTE:
            return bytes_consumed, output_string.decode("ascii")
        elif not 31 < char < 127:
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
