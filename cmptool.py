#!/usr/bin/env python
"""
This is a simple wrapper around the generator to

    - Make sure we eat our own dog food(TM) and try the API.

    - Give us a quick way to run the generator as
      just running Generator.py as a script runs into the
      scripts and packages / modules shall not be mixed rule.
      See https://mail.python.org/pipermail/python-3000/2007-April/006793.html
"""
import argparse
import json
import sys

from generatorcore.generator import Result, calculate_with_default_inputs
from gtest import Gtest

def run_cmd(args):
    # TODO: pass ags in here
    #json.dump(g.result_dict(), indent=4, fp=sys.stdout)
    ags = 'DG000000'
    g = calculate_with_default_inputs(ags=args.ags, year=args.year)
    gt = Gtest()
    gt.set_dict(g.result_dict())
    gt.set_excel('excel/germany_values.json')
    gt.check('t30', 16)

def main():
    parser = argparse.ArgumentParser()
    parser.set_defaults()
    subcmd_parsers = parser.add_subparsers(dest="subcmd")

    cmd_run_parser = subcmd_parsers.add_parser("run", help="Run the generator")
    cmd_run_parser.add_argument("-ags", default="DG000000")
    cmd_run_parser.add_argument("-year", default=2035)
    cmd_run_parser.set_defaults(func=run_cmd)

    args = parser.parse_args()
    if args.subcmd is None:
        parser.print_help()
    else:
        args.func(args)


main()