#!/usr/bin/env python

import base64
from collections import OrderedDict
import decimal
import json
from pathlib import Path
import sys
from typing import Any, List, Union

from shhh import parse, serialise

FAIL = "\033[91m"
ENDC = "\033[0m"


def load_tests(files=None) -> List:
    suites = []
    if not files:
        files = Path("test/tests").glob("*.json")
    for filename in files:
        fh = open(filename)
        suite_json = json.load(fh, parse_float=decimal.Decimal)
        suites.append((filename, suite_json))
    return suites


def run_suite(suite_name: str, suite: List) -> None:
    print("## %s" % suite_name)
    suite_tests = 0
    suite_passed = 0
    for test in suite:
        suite_tests += 1
        parse_success, parsed, parse_fail_reason = test_parse(test)
        ser_success = True
        if not test.get("must_fail", False):
            ser_success, serialised, ser_expected, ser_fail_reason = test_serialise(
                test
            )

        if parse_success and ser_success:
            suite_passed += 1
        else:
            if not parse_success:
                print(f"{FAIL}  * {test['name']}: PARSE FAIL{ENDC}")
                print(f"    - expected: {test.get('expected', 'FAIL')}")
                print(f"    -      got: {walk_json_parse(parsed)}")
                print(f"    -   reason: {parse_fail_reason}")
                if test.get("can_fail", False):
                    print("    - (test failure not critical)")
            if not ser_success:
                print(f"{FAIL} * {test['name']}: SERIALISE FAIL{ENDC}")
                print(f"    - expected: {ser_expected}")
                print(f"    -      got: [{serialised}]")
                print(f"    -   reason: {ser_fail_reason}")

    print(f"-> {suite_passed} of {suite_tests} passed.")
    print()
    return suite_tests, suite_passed


def test_parse(test: dict) -> Union[bool, Any, str]:
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
        sys.stderr.write(f"*** TEST ERROR in {test['name']}\n")
        raise
    if test.get("must_fail", False):
        test_success = not parse_success
    else:
        test_success = test["expected"] == walk_json_parse(parsed)
    return test_success, parsed, parse_fail_reason


def test_serialise(test: dict) -> Union[bool, str, str, str]:
    expected = test.get("canonical", test["raw"])
    output = None
    serialise_fail_reason = None
    input_data = walk_json_ser(test["expected"])
    try:
        output = serialise(input_data, test["header_type"])
    except ValueError as why:
        serialise_fail_reason = why
    except Exception:
        sys.stderr.write(f"*** TEST ERROR in {test['name']}\n")
        raise
    test_success = expected == [output]
    return test_success, output, expected, serialise_fail_reason


def walk_json_parse(thing: Any) -> Any:
    out = thing
    if type(thing) in [OrderedDict, dict]:
        out = {k: walk_json_parse(thing[k]) for k in thing}
    if type(thing) in [list, tuple]:
        out = [walk_json_parse(i) for i in thing]
    if type(thing) is bytes:
        out = base64.b32encode(thing).decode("ascii")
    return out

def walk_json_ser(thing: Any) -> Any:
    out = thing
    if type(thing) is dict:
        out = {k: walk_json_ser(thing[k]) for k in thing}
    if type(thing) is list:
        out = [walk_json_ser(i) for i in thing]
    if isinstance(thing, str):
        if thing.endswith("=*"):
            out = base64.b32decode(thing)
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
