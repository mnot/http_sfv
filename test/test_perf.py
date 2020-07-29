#!/usr/bin/env pypy3

import timeit

import http_sfv as sfv



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
    i = 100000
    return timeit.timeit(
        f"sfv.structures['{field_type}']().parse(b'{structure}')",
        setup='import time; time.sleep(2)',
        globals=globals(),
        number=i
    )


if __name__ == "__main__":
    for test_structure, field_type, name in perf_structures:
        times = time_parse(test_structure, field_type)
        print(f"* {name:25.25s}: {times:4.3f}s")
