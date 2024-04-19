#!/usr/bin/env python3
import argparse
import sys
import src.helpers.exit_handler
from src.create import create
from src.analyze import analyze
from src.run import Run
from src.helpers.colors import *

def add_argument_customfilename(subparser):
    subparser.add_argument('--path', type=str, default=None, help='Set the custom full file name of the created exercise (by default ./data/*.txt).')
def add_argument_path(subparser):
    subparser.add_argument('path', type=str, help="Path to file.")
def add_stylemode_arguments(subparser):
    subparser.add_argument('style', choices=['abacus', 'mental'], help='Calculate using an abacus or mentally.')
    subparser.add_argument('mode', choices=['training', 'exam'], type=str, help="Training or exam.")
def add_arithmetic_args(subparser):
    subparser.add_argument('first',  type=float, help='First number of the progression.')
    subparser.add_argument('diff',   type=float, help='The difference between the numbers.')
    subparser.add_argument('length', type=int, help='The length of the progression.')
    add_argument_customfilename(subparser)
def add_randomcover_args(subparser):
    help_params =r"""params = "<sequence> <sequence> ..."

  определяет параметры для последовательностей из которых будет состоять выражение.\n
  параметры должны быть указаны хотябы для одной последовательности.
  параметры для разных последовательностей разделяются пробельными символами.
  параметры для каждой последовательности состоят из двух секций:
  обязательные аргументы и необязательные.
  если указываются необязательных аргументы - они отделяются через двоеточие:

    seq = "<required>:<optional>"

<required>:
  обязательные параметры (кроме <lenght>), отделяются друг от друга запятыми,
  указываются в строгом порядке:
  <start-number> (указывавется только для первой последовательности):
    любое число, влючая отрицательные и десятичные дроби.
    r - выбрать рандомно из указанного ниже диапазона.
  <operands>:
    какие использовать операнды. варинаты: "+", "-", "*", "/".
    при указании нескольких операндов будут выбираться рандомно
    для каждого нового числа.
    после каждого операнда можно указать приоритет
    в виде любого натурального числа (по умолчанию 1).
  <range>:
  <lenght> (для kind=cover необятельный)
    длина последовательности, где <lenght> любое натуральное число.
    для kind=cover необзятельный, после того как все комбинации будут
    подобраны генерировать числа рандомно.

<optional>:
  необязательные параметры, друг от друга не отделяются,
  указываются в случайном порядке:
  "n" (allow-negative, поумолчанию отлючено):
    если start-number >= 0 разрешить уходить в минус.
    если start-number  < 0 разрешить уходить меньше чем был start-number.
  ".x%%y" (float, поумолчанию отлючено):
    рандомно добавлять десятичные дроби с точностью до "x" знаков после запятой,
    где "x" любое натуральное число. поумолчанию - нет.
    в конце можно указать вероятность в процентах через "%%y",
    где "y" натуральное число от 0 до 100 (по умолчанию %%10).
  "<" (roundtrip, поумолчанию отлючено):
    добавить вконец копию инвертированной версии получившегося выражения:
      - отзеркалить последовательность чисел
      - преобразовать + в -, * в / и наоборот

примеры использования:
  "0,+,1-99,100",
  "r,+-,142-9345,5000",
  "34,+2-1,2-13,12",
  "-34,-+2,0-9,5",
  "0,+,1-9,5",
  "0,+,1-9,5:<",
  "0,+,1-9,5:n",
  "0,+,1-9,5:n.2",
  "0,+,1-9,5:n.3%%50",
  "0,+,1-9,5:n.4%%10<",
  "0,+,1-99,100   +-,142-9345,5000:n.3%%50 +2-1,2-13,12:<",
  "0,+,1-99:<     +-,1-999:n.2            *2/,1-9,10"
"""
    subparser.add_argument('params', type=str, help=help_params)
    add_argument_customfilename(subparser)

def main():
    parser = argparse.ArgumentParser(description='Soroban exercise management system.')
    # <command>
    p_command = parser.add_subparsers(dest='command', required=True, help='Command to perform.')
    p_create  = p_command.add_parser('create', help='Create a new exercise.')
    p_analyze = p_command.add_parser('analyze', help='Analyze an exercise.')
    p_run     = p_command.add_parser('run', help='Run an existing exercise.')
    p_runnew  = p_command.add_parser('run-new', help='Create, analyze and run a new exercise.')
    # create
    p_create_kind = p_create.add_subparsers(dest='kind', required=True, help='Type of exercise.')
    p_create_arithmetic = p_create_kind.add_parser('arithmetic', help='An arithmetic progression.')
    p_create_random     = p_create_kind.add_parser('random', help='Generate numbers randomly.',
                                                   formatter_class=argparse.RawTextHelpFormatter)
    p_create_cover      = p_create_kind.add_parser('cover-units', help='Covering all possible combinations of the category of units.',
                                                   formatter_class=argparse.RawTextHelpFormatter)
    add_arithmetic_args(p_create_arithmetic)
    add_randomcover_args(p_create_random)
    add_randomcover_args(p_create_cover)
    # analyze
    add_argument_path(p_analyze)
    # run
    add_stylemode_arguments(p_run)
    add_argument_path(p_run)
    # run-new
    add_stylemode_arguments(p_runnew)
    p_runnew_kind = p_runnew.add_subparsers(dest='kind', required=True, help='Type of exercise.')
    p_runnew_arithmetic = p_runnew_kind.add_parser('arithmetic', help='An arithmetic progression.')
    p_runnew_random     = p_runnew_kind.add_parser('random', help='Generate numbers randomly.',
                                                   formatter_class=argparse.RawTextHelpFormatter)
    p_runnew_cover      = p_runnew_kind.add_parser('cover-units', help='Covering all possible combinations of the category of units.',
                                                   formatter_class=argparse.RawTextHelpFormatter)
    add_arithmetic_args(p_runnew_arithmetic)
    add_randomcover_args(p_runnew_random)
    add_randomcover_args(p_runnew_cover)

    args = parser.parse_args()
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
