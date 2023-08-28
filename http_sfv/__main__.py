#!/usr/bin/env python3

import argparse
import sys

from . import parse
from .util import to_json


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
structure.add_argument(
    "-n",
    "--name",
    dest="field_name",
    action="store",
    help="Field name",
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
    input_bytes = input_string.encode("utf-8")
    if args.field_type:
        field = parse(input_bytes, tltype=args.field_type)
    else:
        field = parse(input_bytes, name=args.field_name)
    print(to_json(field, sort_keys=True, indent=4))
except ValueError as why:
    sys.stderr.write(f"VALUE: {input_string.strip()}\n")
    sys.stderr.write(f"FAIL: {why}\n")
    sys.exit(1)
