
import base64
from collections import OrderedDict
from datetime import datetime
import decimal
import json
from pathlib import Path
import sys
from typing import Any, List, Union

from http_sfv import parse_text, ser_text, Token, DisplayString

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

        if False and not test.get("must_fail", False):
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
    try:
        field_value = b", ".join([v.encode('utf-8') for v in test["raw"]])
        structure = parse_text(field_value, tltype=test["header_type"])
        parse_success = True
    except ValueError as why:
        parse_fail_reason = why.args
        structure = {}
    except Exception as why:
        sys.stderr.write(f"*** TEST ERROR in {test['name']}\n")
        raise
    if test.get("must_fail", False):
        test_success = not parse_success
    else:
        test_success = test["expected"] == norm(structure)
    return test_success, norm(structure), parse_fail_reason

def norm(structure: Any) -> Any:
    if isinstance(structure, dict):
        structure = [[k, adjust(v)] for k,v in structure.items()]
    elif isinstance(structure, list):
        structure = [adjust(i) for i in structure]
    else:
        structure = adjust(structure)
    return json.loads(json.dumps(structure, default=objhandler), parse_float=decimal.Decimal)

def adjust(thing: Any) -> Any:
    if isinstance(thing, tuple) and len(thing) == 2:
        if isinstance(thing[0], decimal.Decimal):
            thing = [float(thing[0]), thing[1]]
        if isinstance(thing[1], decimal.Decimal):
            thing = [thing[0], float(thing[1])]
        if isinstance(thing[0], list):
            thing = [[adjust(i) for i in thing[0]], thing[1]]
        if isinstance(thing[1], dict):
            thing = [thing[0], [adjust((k,v)) for k,v in thing[1].items()]]
    return thing

def objhandler(inobj: Any) -> dict:
    if isinstance(inobj, Token):
        return {
            "__type": "token",
            "value": str(inobj)
        }
    if isinstance(inobj, bytes):
        return {
            "__type": "binary",
            "value": base64.b32encode(inobj).decode('ascii')
        }
    if isinstance(inobj, datetime):
        return {
            "__type": "date",
            "value": inobj.timestamp()
        }
    if isinstance(inobj, DisplayString):
        return {
            "__type": "displaystring",
            "value": str(inobj)
        }

def test_serialise(test: dict) -> Union[bool, str, str, str]:
    expected = test.get("canonical", test["raw"])
    output = None
    serialise_fail_reason = None
    try:
        output = ser_text(test["expected"])
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
