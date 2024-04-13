#!/usr/bin/env python3
import argparse
import sys
import src.helpers.exit_handler
from src.create import create
from src.analyze import analyze
from src.run import Run

def create_subparser_for_create_command(subparsers, parent_parser):
    parser_create = subparsers.add_parser("create", help="Create a new exercise.")
    create_subparsers = parser_create.add_subparsers(dest="kind", required=True, help="kind for creating exercise.")
    # Shared arguments for 'random' and 'cover-units' kind
    shared_parser = argparse.ArgumentParser(add_help=False)
    shared_parser.add_argument("operations", choices=["plus", "minus", "plus-minus", "plus-minus-roundtrip"], help="Arithmetic operations to use.")
    shared_parser.add_argument("range", help="The range of possible values for numbers.")

    # 'arithmetic' kind specific
    parser_arithmetic = create_subparsers.add_parser("arithmetic", parents=[parent_parser], help="Create an arithmetic progression.")
    parser_arithmetic.add_argument("first", type=int, help="First number of the progression.")
    parser_arithmetic.add_argument("length", type=int, help="Amount of numbers.")
    # 'random' kind specific
    parser_random = create_subparsers.add_parser("random", parents=[shared_parser, parent_parser], help="Generate numbers randomly.")
    parser_random.add_argument("length", type=int, help="Amount of numbers.")
    # 'cover-units' kind
    create_subparsers.add_parser("cover-units", parents=[shared_parser, parent_parser], help="Covering all possible combinations of the category of units.")

def create_subparser_for_runnew_command(subparsers, parent_parser):
    parser_create = subparsers.add_parser("run-new", help="Create, analyze and run a new exercise.")
    runnew_subparsers = parser_create.add_subparsers(dest="kind", required=True, help="kind for creating exercise.")
    # Shared arguments for 'random' and 'cover-units' kind
    shared_parser = argparse.ArgumentParser(add_help=False)
    shared_parser.add_argument("operations", choices=["plus", "minus", "plus-minus", "plus-minus-roundtrip"], help="Arithmetic operations to use.")
    shared_parser.add_argument("range", help="The range of possible values for numbers.")

    # 'arithmetic' kind specific
    parser_arithmetic = runnew_subparsers.add_parser("arithmetic", parents=[parent_parser], help="Create an arithmetic progression.")
    parser_arithmetic.add_argument("first", type=int, help="First number of the progression.")
    parser_arithmetic.add_argument("length", type=int, help="Amount of numbers.")
    # 'random' kind specific
    parser_random = runnew_subparsers.add_parser("random", parents=[shared_parser, parent_parser], help="Generate numbers randomly.")
    parser_random.add_argument("length", type=int, help="Amount of numbers.")
    # 'cover-units' kind
    runnew_subparsers.add_parser("cover-units", parents=[shared_parser, parent_parser], help="Covering all possible combinations of the category of units.")

def main():
    parser = argparse.ArgumentParser(description="Soroban exercise management system.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Command to perform.")
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("name", nargs="?", help="Name for the new exercise.")
    # 'create' command
    create_subparser_for_create_command(subparsers, parent_parser)
    # 'analyze' command
    parser_analyze = subparsers.add_parser("analyze", help="Analyze an exercise.")
    parser_analyze.add_argument("path", help="Path to the file.")
    # 'run' command
    parser_run = subparsers.add_parser("run", help="Run an existing exercise.")
    parser_run.add_argument("path", help="Path to the file.")
    # 'run-new' command
    create_subparser_for_runnew_command(subparsers, parent_parser)

    args = parser.parse_args()
    if args.command == 'create':
        create(args)
    elif args.command == 'analyze':
        analyze(args.path)
    elif args.command == 'run':
        Run(args.path)
    elif args.command == 'run-new':
        path = create(args)
        analyze(path)
        Run(path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
