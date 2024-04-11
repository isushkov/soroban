#!/usr/bin/env python3
import argparse
import sys
import src.helpers.exit_handler
from src.create import create_random, create_cover_units, create_arithmetic
from src.analyze import analyze
from src.run import Run

# main.py <command>
#         create <type>
#                random <operations> <range> <name>
#                       plus
#                       minus
#                       plus-minus
#                       linear-plus-minus
#                cover-units <operations> <range> <name>
#                            plus
#                            minus
#                            plus-minus
#                            linear-plus-minus
#                arithmetic <first> <length> <name>
#         analyze <name>
#         run <name>
#         run-new <like-create>
def create_subparser_for_create_command(subparsers, parent_parser):
    parser_create = subparsers.add_parser("create", help="Create a new exercise.")
    create_subparsers = parser_create.add_subparsers(dest="type", required=True, help="Type for creating exercise.")
    # Shared arguments for 'random' and 'cover-units' types
    shared_parser = argparse.ArgumentParser(add_help=False)
    shared_parser.add_argument("operations", choices=["plus", "minus", "plus-minus", "linear-plus-minus"], help="Arithmetic operations to use.")
    shared_parser.add_argument("range", help="Range of possible operand values.")
    # 'random' type specific
    parser_random = create_subparsers.add_parser("random", parents=[shared_parser, parent_parser], help="Random type for creating exercise.")
    parser_random.add_argument("length", type=int, help="Number of terms.")
    # 'cover-units' type
    create_subparsers.add_parser("cover-units", parents=[shared_parser, parent_parser], help="Cover-units type for creating exercise.")
    # 'arithmetic' type specific
    parser_arithmetic = create_subparsers.add_parser("arithmetic", parents=[parent_parser], help="Arithmetic type for creating exercise.")
    parser_arithmetic.add_argument("first", type=int, help="First number of the progression.")
    parser_arithmetic.add_argument("length", type=int, help="Length of the progression.")
def create_subparser_for_runnew_command(subparsers, parent_parser):
    parser_create = subparsers.add_parser("run-new", help="Run a new exercise.")
    runnew_subparsers = parser_create.add_subparsers(dest="type", required=True, help="Type for creating exercise.")
    # Shared arguments for 'random' and 'cover-units' types
    shared_parser = argparse.ArgumentParser(add_help=False)
    shared_parser.add_argument("operations", choices=["plus", "minus", "plus-minus", "linear-plus-minus"], help="Arithmetic operations to use.")
    shared_parser.add_argument("range", help="Range of possible operand values.")
    # 'random' type specific
    parser_random = runnew_subparsers.add_parser("random", parents=[shared_parser, parent_parser], help="Random type for creating exercise.")
    parser_random.add_argument("length", type=int, help="Number of terms.")
    # 'cover-units' type
    runnew_subparsers.add_parser("cover-units", parents=[shared_parser, parent_parser], help="Cover-units type for creating exercise.")
    # 'arithmetic' type specific
    parser_arithmetic = runnew_subparsers.add_parser("arithmetic", parents=[parent_parser], help="Arithmetic type for creating exercise.")
    parser_arithmetic.add_argument("first", type=int, help="First number of the progression.")
    parser_arithmetic.add_argument("length", type=int, help="Length of the progression.")

def main():
    parser = argparse.ArgumentParser(description="Exercise management system.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Command to perform.")
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("name", nargs="?", help="Name for the new exercise.")
    # 'create' command
    create_subparser_for_create_command(subparsers, parent_parser)
    # 'analyze' command
    parser_analyze = subparsers.add_parser("analyze", help="Analyze an exercise.")
    parser_analyze.add_argument("name", help="Name of the exercise to analyze.")
    # 'run' command
    parser_run = subparsers.add_parser("run", help="Run an existing exercise.")
    parser_run.add_argument("name", help="Name of the exercise to run.")
    # 'run-new' command
    create_subparser_for_runnew_command(subparsers, parent_parser)

    args = parser.parse_args()
    if args.command == 'create':
        if args.type == 'arithmetic':
            create_arithmetic(args.first, args.length, args.name)
        elif args.type == 'random':
            create_random(args.operations, args.length, args.range, args.name)
        elif args.type == 'cover-units':
            create_cover_units(args.operations, args.range, args.name)
    elif args.command == 'analyze':
        analyze(args.name)
    elif args.command == 'run-new':
        if args.type == 'random':
            name = create_random(args.operations, args.length, args.range, args.name)
        elif args.type == 'cover-units':
            name = create_cover_units(args.operations, args.range, args.name)
        elif args.type == 'arithmetic':
            name = create_arithmetic(args.first, args.length, args.name)
        analyze(name)
        Run(name)
    elif args.command == 'run':
        # TODO: ...
        fexit('TODO: ...')
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
