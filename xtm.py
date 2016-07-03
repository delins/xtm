#!/usr/bin/python3

import argparse
from xtm.parser import TraceParser
from xtm.filters import *
from xtm.visitors.print_tree import TreePrintingVisitor


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(dest='action')
    sub_parsers.required = True # Set required because of what is probably a bug in (some) Python versions: http: // bugs.python.org / issue9253  # msg186387

    # print_parent_parser
    # ------------------------------------------------------------------------------------------------------------------
    print_parser_parent = argparse.ArgumentParser(add_help=False)
    print_parser_parent.add_argument('-i',
                                     help='XDebug trace file (required)',
                                     dest='input_file',
                                     required=True)
    print_parser_parent.add_argument('-d',
                                     help='filter definition file',
                                     dest='filter_def_file')
    print_parser_parent.add_argument('-r',
                                     help='output relative depth instead of the default absolute',
                                     dest='relative_depth',
                                     action='store_true')
    print_parser_parent.add_argument('-m',
                        help='print meta information',
                        dest='print_meta',
                        action='store_true')

    # tree_parser
    # ------------------------------------------------------------------------------------------------------------------
    tree_parser = sub_parsers.add_parser('printtree',
                                         help='Print tree. Accepts multiple formatting options.',
                                         parents=[print_parser_parent])

    # csv_parser (not implemented beyond the command line subcommand!
    # ------------------------------------------------------------------------------------------------------------------
    csv_parser = sub_parsers.add_parser('printcsv',
                                        help='Print CSV. Is used to easily filter the CSV. Not implemented yet.',
                                        parents=[print_parser_parent])

    args = parser.parse_args()

    coverage_parser = TraceParser(filename=args.input_file)
    coverage_parser.parse()

    filter_config = None
    if args.filter_def_file:
        with open(args.filter_def_file, 'r') as f:
            filter_config = FilterConfig(f.read())
    if not filter_config:
        filter_config = FilterConfig()

    if args.action == 'printtree':
        visitor = TreePrintingVisitor(filter_config=filter_config, relative_depth=args.relative_depth)

        if args.print_meta:
            print(coverage_parser.format_meta())

        coverage_parser.root_record.visit(visitor)

    elif args.sub_command == 'printcsv':
        print('not implemented yet')