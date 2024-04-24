#!/usr/bin/env python3

import argparse
import sys
from src.study import study
from src.create import create
from src.analyze import analyze
from src.run import Run
import src.helper as h
from src.helpers.fo import Fo as fo
import src.helpers.exit_handler

def add_arg_params(subparser):
    subparser.add_argument('params', type=str, help=fo.txt2str('./src/_help-params.txt'))
def add_arg_path(subparser):
    subparser.add_argument('path', type=str, help="Path to file.")
def add_args_style_mode(subparser):
    subparser.add_argument('style', choices=['abacus', 'mental'], help='Calculate using an abacus or mentally.')
    h = """A training session or exam for a specific exercise
    or a collection of exercises with pre-defined modes (training and exam)
    and time to successfully complete further."""
    subparser.add_argument('mode', choices=['training', 'exam', 'study'], type=str, help=h)
def add_optarg_path(subparser):
    subparser.add_argument('--path', type=str, default=None, help='Set the custom full file name of the created exercise (by default ./data/*.txt).')
def add_optarg_username(subparser):
    subparser.add_argument('--user-name', type=str, default=None, help='User-name to save and track records')

def main():
    parser = argparse.ArgumentParser(description='Soroban exercise management system.')
    # <command>
    p_command = parser.add_subparsers(dest='command', required=True, help='Command to perform.')
    # create
    p_create = p_command.add_parser('create', help='Create a new exercise.')
    add_arg_params(p_create)
    add_optarg_path(p_create)
    # analyze
    p_analyze = p_command.add_parser('analyze', help='Analyze an exercise.')
    add_arg_path(p_analyze)
    # run
    p_run = p_command.add_parser('run', help='Run an existing exercise.')
    add_args_style_mode(p_run)
    add_arg_path(p_run)
    add_optarg_username(p_runnew)
    # run-new
    p_runnew = p_command.add_parser('run-new', help='Create, analyze and run a new exercise.')
    add_args_style_mode(p_runnew)
    add_arg_params(p_runnew)
    add_optarg_path(p_runnew)
    add_optarg_username(p_runnew)

    args = parser.parse_args()
    if args.command == 'create':
        path = create(args)
        analyze(path)
    elif args.command == 'analyze':
        analyze(args.path)
    else:
        user_name = args.user_name.strip()[:6] or False
        if args.style == 'mental':
            h.todo('style mental')
        else:
            if args.mode == 'study':
                user_name, mode, params = study(user_name)
                path = create(path=False, params=params)
                analyze(path)
                Run(path, mode, user_name)
            else:
                if args.command == 'run':
                    analyze(args.path)
                    Run(path, args.mode, user_name)
                elif args.command == 'run-new':
                    path = create(args.path, args.params)
                    analyze(path)
                    Run(path, args.mode, user_name)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
