#!/usr/bin/env python

import base64
from collections import OrderedDict
import json
from pathlib import Path
import sys
from typing import Any, List

from shhh import parse


def load_tests(files=None) -> List:
    suites = []
    if not files:
        files = Path("test/tests").glob("*.json")
    for filename in files:
        fh = open(filename)
        suite_json = json.load(fh)
        suites.append((filename, suite_json))
    return suites

def run_suite(suite_name: str, suite: List) -> None:
    print("*** %s" % suite_name)
    for test in suite:
        parsed = None
        parse_success = False
        parse_fail_reason = None
        test_success = False
        sys.stdout.write("* %s: " % test["name"])
        try:
            parsed = parse(", ".join(test["raw"]), test["header_type"])
            parse_success = True
        except ValueError as why:
            parse_fail_reason = why
        if test["expected"] is False:
            test_success = not parse_success
        else:
            test_success = test["expected"] == walk_json(parsed)
        print(test_success and "PASS" or "FAIL")
        if not test_success:
            print("  - expected: %s" % (test["expected"] or "FAIL"))
            print("  -      got: %s" % walk_json(parsed))
    print()


def walk_json(thing: Any) -> Any:
    out = thing
    if type(thing) is OrderedDict:
        out = {k: walk_json(thing[k]) for k in thing}
    if type(thing) is list:
        out = [walk_json(i) for i in thing]
    if type(thing) is tuple:
        out = list(thing)
    if type(thing) is bytes:
        out = base64.b32encode(thing).decode('ascii')
    return out

if __name__ == "__main__":
    suites = load_tests()
    for filename, suite in suites:
        run_suite(filename, suite)
