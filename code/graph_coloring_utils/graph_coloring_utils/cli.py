#!/usr/bin/python

"""Graph Coloring Utils CLI
Usage:
  gcutils distinct_4_colorings_for_cycle <v> [--count | --calc | --compare]

Options:
  -h --help               Show help info
  --version               Show version
                          (you will need to have 'syk --test up' running)
  --count                 Count the number of colorings individually
  --calc                  Count the number of colorings using a formula
  --compare               Compare the --count and --calc values

Description:
  distinct_4_colorings_for_cycle    Given a chordless cycle with v vertices,
                                    this will return all of the distinct,
                                    valid 4 colorings of that cycle
"""
from docopt import docopt
from .__init__ import __version__

from .find_distinct_4_colorings_for_cycle import (
    find_distinct_4_colorings_for_cycle
)
from .calc_distinct_4_colorings_for_cycle import (
    calc_distinct_4_colorings_for_cycle
)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_fail(msg):
    print(bcolors.FAIL + msg + bcolors.ENDC)


def print_success(msg):
    print(bcolors.OKGREEN + msg + bcolors.ENDC)


def main():
    args = docopt(__doc__, version=__version__)

    if args['distinct_4_colorings_for_cycle']:
        v = None
        non_int = False

        try:
            v = int(args['<v>'])
        except Exception as e:
            non_int = True

        if non_int or v < 3:
            print_fail("<v> must be an integer greater or equal to 3")
            return

        if args['--count']:
            colorings = find_distinct_4_colorings_for_cycle(v)
            print(len(colorings))
        elif args['--calc']:
            calced_colorings = calc_distinct_4_colorings_for_cycle(v)
            print(calced_colorings)
        elif args['--compare']:
            colorings = find_distinct_4_colorings_for_cycle(v)
            calced_colorings = calc_distinct_4_colorings_for_cycle(v)
            counted_colorings = len(colorings)
            print('Counted: ', counted_colorings)
            print('Calculated: ', calced_colorings)
            if counted_colorings == calced_colorings:
                print_success('Equal')
            else:
                print_fail('Not equal')

        else:
            colorings = find_distinct_4_colorings_for_cycle(v)
            for coloring in colorings:
                print(coloring)
