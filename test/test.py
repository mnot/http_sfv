#!/usr/bin/env python3

import base64
from collections import OrderedDict
import decimal
import json
from pathlib import Path
import sys
from typing import Any, List, Union

from http_sfv import structures

FAIL = "\033[91m"
WARN = "\033[93m"
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
        if parse_success:
            suite_passed += 1
        else:
            if test.get("can_fail", False):
                print(f"{WARN}  * {test['name']}: PARSE FAIL (non-critical){ENDC}")
                suite_passed += 1
            else:
                print(f"{FAIL}  * {test['name']}: PARSE FAIL{ENDC}")
            print(f"    -      raw: {test['raw']}")
            print(f"    - expected: {test.get('expected', 'FAIL')}")
            print(f"    -      got: {parsed}")
            if parse_fail_reason:
                print(f"    -   reason: {parse_fail_reason}")

        if not test.get("must_fail", False):
            suite_tests += 1
            ser_success, serialised, ser_expected, ser_fail_reason = test_serialise(
                test
            )
            if ser_success:
                suite_passed += 1
            else:
                print(f"{FAIL} * {test['name']}: SERIALISE FAIL{ENDC}")
                print(f"    - expected: {ser_expected}")
                print(f"    -      got: ['{serialised}']")
                if ser_fail_reason:
                    print(f"    -   reason: {ser_fail_reason}")

    print(f"-> {suite_passed} of {suite_tests} passed.")
    print()
    return suite_tests, suite_passed


def test_parse(test: dict) -> Union[bool, Any, str]:
    parsed = None
    parse_success = False
    parse_fail_reason = None
    test_success = False
    field = structures[test["header_type"]]()
    try:
        field.parse(b", ".join([v.encode('utf-8') for v in test["raw"]]))
        parse_success = True
    except ValueError as why:
        parse_fail_reason = why.args
    except Exception:
        sys.stderr.write(f"*** TEST ERROR in {test['name']}\n")
        raise
    if test.get("must_fail", False):
        test_success = not parse_success
    else:
        test_success = test["expected"] == field.to_json()
    return test_success, field.to_json(), parse_fail_reason


def test_serialise(test: dict) -> Union[bool, str, str, str]:
    expected = test.get("canonical", test["raw"])
    output = None
    serialise_fail_reason = None
    field = structures[test["header_type"]]()
    field.from_json(test["expected"])
    try:
        output = str(field)
    except ValueError as why:
        serialise_fail_reason = why.args[0]
    except Exception:
        sys.stderr.write(f"*** TEST ERROR in {test['name']}\n")
        raise
    if output is None:
        test_success = expected == []
    else:
        test_success = expected == [output]
    return test_success, output, expected, serialise_fail_reason


if __name__ == "__main__":
    import argparse

    argparser = argparse.ArgumentParser(description="Run tests.")
    argparser.add_argument(
        "files",
        metavar="filename",
        type=str,
        nargs="*",
        help="a JSON file containing tests",
    )
    args = argparser.parse_args()
    suites = load_tests(args.files)
    total_tests = 0
    total_passed = 0
    for filename, suite in suites:
        tests, passed = run_suite(filename, suite)
        total_tests += tests
        total_passed += passed
    print("TOTAL: %s of %s passed." % (total_passed, total_tests))
    if total_passed < total_tests:
        sys.exit(1)
