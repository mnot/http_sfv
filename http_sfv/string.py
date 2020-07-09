from typing import Tuple

from .util import remove_char

DQUOTE = '"'
BACKSLASH = "\\"
DQUOTEBACKSLASH = set(DQUOTE + BACKSLASH)


def parse_string(input_string: str) -> Tuple[str, str]:
    output_string = []
    if not input_string or input_string[0] is not DQUOTE:
        raise ValueError(
            f"First character of string is not DQUOTE at: {input_string[:10]}"
        )
    input_string = input_string[1:]
    while input_string:
        input_string, char = remove_char(input_string)
        if char is BACKSLASH:
            if not input_string:
                raise ValueError(
                    f"Last character of input was a backslash at: {input_string[:10]}"
                )
            input_string, next_char = remove_char(input_string)
            if next_char not in DQUOTEBACKSLASH:
                raise ValueError(
                    f"Backslash before disallowed character '{next_char}' at: {input_string[:10]}"
                )
            output_string.append(next_char)
        elif char == DQUOTE:
            return input_string, "".join(output_string)
        elif not 31 < ord(char) < 127:
            raise ValueError(
                f"String contains disallowed character at: {input_string[:10]}"
            )
        else:
            output_string.append(char)
    raise ValueError(
        f"Reached end of input without finding a closing DQUOTE at: {input_string[:10]}"
    )


def ser_string(inval: str) -> str:
    if not all(31 < ord(char) < 127 for char in inval):
        raise ValueError("String contains disallowed characters.")
    output = ""
    output += DQUOTE
    for char in inval:
        if char in BACKSLASH + DQUOTE:
            output += BACKSLASH
        output += char
    output += DQUOTE
    return output
