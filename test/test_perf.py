#!/usr/bin/env pypy3

import locale
import time
import timeit

import http_sfv as sfv

locale.setlocale(locale.LC_ALL, "")

digits = 9
unit = 'ns'
i = 50000
wait = 2

perf_structures = [
    ('"abcdefghijklmnopqrstuvwxyz"', 'item', 'String (simple)'),
    ('abdefghijklmnopqrstuvwxyz', 'item', 'Token (simple)'),
    ('123456789012345', 'item', 'Integer (simple)'),
    ('123456789012.345', 'item', 'Decimal (simple)'),
    ('?0', 'item', 'Boolean (false)'),
    ('?1', 'item', 'Boolean (true)'),
    (':aGVsbG8=:', 'item', 'Byte Sequence (simple)'),
    ('abcd, efg, hi, jk, lmno, p, qrs, tuv, w, x, y, z', 'list', 'List (simple)'),
    ('abcd; efg=hi; jk=lmno, p; qrs=tuv; w=x, y, z', 'list', 'List (parameters)'),
    ('abcd=efg, hi, jk=lmno, p, qrs=tuv, w=y, y=z', 'dictionary', 'Dictionary (simple)'),
    ('abcd=efh;hi=jk, lmno;p, qrs=tuv;w=x;y=z', 'dictionary', 'Dictionary (parameters)')
]


def time_parse(structure, field_type):
    return int(timeit.timeit(
        f"sfv.structures['{field_type}']().parse('{structure}')",
        setup='import time; time.sleep(2)',
        globals=globals(),
        number=i
    ) / i * (10 ** digits))


if __name__ == "__main__":
    for test_structure, field_type, name in perf_structures:
        time.sleep(wait)
        times = time_parse(test_structure, field_type)
        print(f"* {name:25.25s} {times:{digits}n} {unit}")
