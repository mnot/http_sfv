#!/usr/bin/env python

import base64
from collections import OrderedDict
import json
from pathlib import Path
import sys
from typing import Any, List

from shhh import parse

FAIL = '\033[91m'
ENDC = '\033[0m'

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
    print("## %s" % suite_name)
    suite_tests = 0
    suite_passed = 0
    for test in suite:
        suite_tests += 1
        parsed = None
        parse_success = False
        parse_fail_reason = None
        test_success = False
        try:
            parsed = parse(", ".join(test["raw"]), test["header_type"])
            parse_success = True
        except ValueError as why:
            parse_fail_reason = why
        except Exception:
            sys.stderr.write("*** TEST ERROR in %s\n" % test["name"])
            raise
        if test.get("must_fail", False):
            test_success = not parse_success
        else:
            test_success = test["expected"] == walk_json(parsed)
        if test_success:
            suite_passed += 1
        else:
            print("%s  * %s: FAIL%s" % (FAIL, test["name"], ENDC))
            print("    - expected: %s" % test.get("expected", "FAIL"))
            print("    -      got: %s" % walk_json(parsed))
            print("    -   reason: %s" % parse_fail_reason)
        if not test_success and test.get("can_fail", False):
            print("    - (test failure not critical)")
            suite_passed += 1
    print("-> %s of %s passed." % (suite_passed, suite_tests))
    print()
    return suite_tests, suite_passed


def walk_json(thing: Any) -> Any:
    out = thing
    if type(thing) in [OrderedDict, dict]:
        out = {k: walk_json(thing[k]) for k in thing}
    if type(thing) in [list, tuple]:
        out = [walk_json(i) for i in thing]
    if type(thing) is bytes:
        out = base64.b32encode(thing).decode('ascii')
    return out

if __name__ == "__main__":
    suites = load_tests()
    total_tests = 0
    total_passed = 0
    for filename, suite in suites:
        tests, passed = run_suite(filename, suite)
        total_tests += tests
        total_passed += passed
    print("TOTAL: %s of %s passed." % (total_passed, total_tests))
    if total_passed < total_tests:
        sys.exit(1)
