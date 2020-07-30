#!/usr/bin/env python3

import argparse
import json
import sys

from . import structures


parser = argparse.ArgumentParser(
    description="Validate and show data model of a Structured Field Value."
)
structure = parser.add_mutually_exclusive_group(required=True)
structure.add_argument(
    "-d",
    "--dictionary",
    dest="field_type",
    action="store_const",
    const="dictionary",
    help="Dictionary field",
)
structure.add_argument(
    "-l",
    "--list",
    dest="field_type",
    action="store_const",
    const="list",
    help="List field",
)
structure.add_argument(
    "-i",
    "--item",
    dest="field_type",
    action="store_const",
    const="item",
    help="Item field",
)

input_source = parser.add_mutually_exclusive_group(required=True)
input_source.add_argument(
    "input_string",
    nargs="?",
    help="The (textual) structured field value. Do not include the field name.",
)
input_source.add_argument(
    "--stdin",
    dest="stdin",
    action="store_true",
    help="Read the structured field value from STDIN.",
)

args = parser.parse_args()

if args.stdin:
    input_string = sys.stdin.read()
else:
    input_string = args.input_string

try:
    field = structures[args.field_type]()
    field.parse(input_string.encode("utf-8"))
    print(json.dumps(field.to_json(), sort_keys=True, indent=4))
except ValueError as why:
    sys.stderr.write(f"VALUE: {input_string.strip()}\n")
    sys.stderr.write(f"FAIL: {why}\n")
    sys.exit(1)
