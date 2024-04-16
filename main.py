#!/usr/bin/env python3
import argparse
import sys
import src.helpers.exit_handler
from src.create import create
from src.analyze import analyze
from src.run import Run

def main():
    parser = argparse.ArgumentParser(description='Soroban exercise management system.')
    # <command>
    command = parser.add_subparsers(dest='command', required=True, help='Command to perform.')
    create  = command.add_parser('create', help='Create a new exercise.')
    analyze = command.add_parser('analyze', help='Analyze an exercise.')
    run     = command.add_parser('run', help='Run an existing exercise.')
    run_new = command.add_parser('run-new', help='Create, analyze and run a new exercise.')
    # create <kind>
    kind = create.add_subparsers(dest='kind', required=True, help='Type of exercise.')
    arithmetic = kind.add_parser('arithmetic', help='An arithmetic progression.')
    ramdom     = kind.add_parser('random', help='Generate numbers randomly.')
    cover      = kind.add_parser('cover-units', help='Covering all possible combinations of the category of units.')
    # create arithmetic [first,diff,length] (name)
    arithmetic.add_argument('first',  type=float, help='First number of the progression.')
    arithmetic.add_argument('diff',   type=float, help='The difference between the numbers.')
    arithmetic.add_argument('length', type=int, help='The length of the progression.')
    # arithmetic.add_argument('name')

    # create random [params] (name)
    ramdom.add_argument('params', type=str, help='Amount of numbers.')
    # ramdom.add_argument('name')

    # create cover [params] (name)
    # analyze [filiname]
    # run <style> <mode> [filiname]
    # run-new <style> <mode> arithmetic [first,diff,length] (name)
    # run-new <style> <mode> random [params] (name)
    # run-new <style> <mode> cover [params] (name)



    # 'cover-units' kind

    # 'analyze' command
    analyze.add_argument('path', help='Path to the file.')

    # 'run' command
    run.add_argument('path', help='Path to the file.')

    # 'run-new' command
    runnew_subparsers = run_new.add_subparsers(dest='kind', required=True, help='kind for creating exercise.')

    # Reusing common parser for 'run-new' kinds
    # 'arithmetic' kind specific

    # 'random' kind specific
    ramdom = runnew_subparsers.add_parser('random', parents=[parent_parser, common_parser], help='Generate numbers randomly.')
    ramdom.add_argument('length', type=int, help='Amount of numbers.')

    # 'cover-units' kind
    runnew_subparsers.add_parser('cover-units', parents=[parent_parser, common_parser], help='Covering all possible combinations of the category of units.')



    args = parser.parse_args()
    print(args)  # Display parsed arguments
    exit()
    if args.command == 'create':
        path = create(args)
        analyze(path)
    elif args.command == 'analyze':
        analyze(args.path)
    elif args.command == 'run':
        analyze(args.path)
        Run(path)
    elif args.command == 'run-new':
        path = create(args)
        analyze(path)
        Run(path)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
