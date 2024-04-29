#!/usr/bin/env python3
import argparse
import sys
from textwrap import dedent
# src
from src.create import create
from src.analyze import analyze
from src.run import run
from src.study import study
# src/helpers
import src.helpers.fo as fo
import src.helpers.exit_handler

def would_like_repeat():
    while True:
        answer = input("Would you like to repeat? (y/n): ").strip().lower()
        if answer == 'y': return True
        elif answer == 'n': return False
        else:
            print("Invalid input. Please enter 'y' for yes or 'n' for no.")
def init_run(args):
    user_name = (args.user.strip()[:6] or False) if args.user else False
    if args.command == 'study':
        study(user_name)
    else:
        if args.style == 'mental':
            c.todo('style mental')
        elif args.command == 'run':
            analyze(args.path)
            run(path, args.mode, user_name)
        else:
            path = create(args.path, args.params)
            analyze(path)
            run(path, args.mode, user_name)
    if not would_like_repeat():
        return
    init_run(args)

def add_arg_params(subparser):
    subparser.add_argument('params', type=str, help=fo.txt2str('./src/_help_params.txt'))
def add_args_style(subparser):
    subparser.add_argument('style', choices=['abacus', 'mental'], help='Calculate using an abacus or mentally.')
def add_arg_path(subparser):
    subparser.add_argument('path', type=str, help="Path to file.")
def add_optarg_path(subparser):
    subparser.add_argument('--path', type=str, default=None, help='Set the custom full file name of the created exercise (by default ./data/*.txt).')
def add_optarg_username(subparser):
    subparser.add_argument('--user', type=str, default=None, help='User-name to save and track records')

def main():
    parser = argparse.ArgumentParser(description='Soroban exercise management system.')
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
    add_arg_path(p_run)
    add_args_style(p_run)
    prun_mode = p_run.add_subparsers(dest='mode', required=True)
    prun_training = prun_mode.add_parser('training', help='A training session.', formatter_class=argparse.RawTextHelpFormatter)
    prun_exam     = prun_mode.add_parser('exam', help='An exercise.', formatter_class=argparse.RawTextHelpFormatter)
    add_arg_params(prun_training)
    add_arg_params(prun_exam)
    add_optarg_username(p_run)
    # run-new
    p_runnew = p_command.add_parser('run-new', help='Create, analyze and run a new exercise.')
    add_args_style(p_runnew)
    prunnew_mode = p_runnew.add_subparsers(dest='mode', required=True)
    prunnew_training = prunnew_mode.add_parser('training', help='A training session.', formatter_class=argparse.RawTextHelpFormatter)
    prunnew_exam     = prunnew_mode.add_parser('exam', help='Pass the exam.', formatter_class=argparse.RawTextHelpFormatter)
    add_arg_params(prunnew_training)
    add_arg_params(prunnew_exam)
    add_optarg_path(p_runnew)
    add_optarg_username(p_runnew)
    # study
    h_study = dedent("""
    A collection of exercises with pre-defined modes (training and exam)
    and time to successfully complete further.
    """)
    p_study = p_command.add_parser('study', help=h_study, formatter_class=argparse.RawTextHelpFormatter)
    add_optarg_username(p_study)

    args = parser.parse_args()
    if args.command == 'create':
        path = create(args.path, args.params)
        analyze(path)
    elif args.command == 'analyze':
        analyze(args.path)
    elif args.command in ['run', 'run-new', 'study']:
        init_run(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
