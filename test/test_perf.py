#!/usr/bin/env pypy3

from cProfile import Profile
import locale
import time
from pstats import Stats
import timeit

import http_sfv as sfv

locale.setlocale(locale.LC_ALL, "")

digits = 9
unit = 'ns'
i = 50000
wait = 2
do_profile = False

perf_structures = [
    ('"abcdefghijklmnopqrstuvwxyz"', 'item', 'String (simple)'),
    ('"abcd"', 'item', 'String (short)'),
    ('"abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz"', 'item', 'String (long)'),
    ('abcdefghijklmnopqrstuvwxyz', 'item', 'Token (simple)'),
    ('abcd', 'item', 'Token (short)'),
    ('abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz', 'item', 'Token (long)'),
    ('123456789012345', 'item', 'Integer (simple)'),
    ('123456789012.345', 'item', 'Decimal (simple)'),
    ('?0', 'item', 'Boolean (false)'),
    ('?1', 'item', 'Boolean (true)'),
    (':YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo=:', 'item', 'Byte Sequence (simple)'),
    ('(abcd efg hijk lmnop), (qrs tuv w x y z)', 'list', 'Inner List'),
    ('abcd, efg, hi, jk, lmno, p, qrs, tuv, w, x, y, z', 'list', 'List (simple)'),
    ('abcd; efg=hi; jk=lmno, p; qrs=tuv; w=x, y, z', 'list', 'List (parameters)'),
    ('abcd=efg, hi, jk=lmno, p, qrs=tuv, w=y, y=z', 'dictionary', 'Dictionary (simple)'),
    ('abcd=efh;hi=jk, lmno;p, qrs=tuv;w=x;y=z', 'dictionary', 'Dictionary (parameters)')
]


def time_parse(structure, field_type):
    return int(
        timeit.timeit(
        f"sfv.structures['{field_type}']().parse(b'{structure}')",
        setup=f"import time; time.sleep({wait})",
        globals=globals(),
        number=i
    ) / i * (10 ** digits))


if __name__ == "__main__":
    for test_structure, field_type, name in perf_structures:
        if do_profile:
            profiler = Profile()
            profiler.runcall(time_parse, test_structure, field_type)
            stats = Stats(profiler)
            stats.strip_dirs()
            stats.sort_stats('cumulative')
            print(f"* {name}")
            stats.print_stats('^(?!timeit)')
            print()
        else:
            times = time_parse(test_structure, field_type)
            print(f"* {name:25.25s} {times:{digits}n} {unit}")
