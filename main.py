#!/usr/bin/env python3
import argparse
import sys
import src.helpers.exit_handler
from src.create import create
from src.analyze import analyze
from src.run import Run

def main():
    help_params ="""params = "<sequence> <sequence> ..."

  определяет параметры для последовательностей из которых будет состоять выражение.
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
  ".x%y" (float, поумолчанию отлючено):
    рандомно добавлять десятичные дроби с точностью до "x" знаков после запятой,
    где "x" любое натуральное число. поумолчанию - нет.
    в конце можно указать вероятность в процентах через "%y",
    где "y" натуральное число от 0 до 100 (по умолчанию %10).
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
  "0,+,1-9,5:n.3%50",
  "0,+,1-9,5:n.4%10<",
  "0,+,1-99,100   +-,142-9345,5000:n.3%50 +2-1,2-13,12:<",
  "0,+,1-99:<     +-,1-999:n.2            *2/,1-9,10"
"""

    parser = argparse.ArgumentParser(description='Soroban exercise management system.')
    это должно быть style=abacus или style=mental:
    # <style>
    style = parser.add_subparsers(dest='style', required=True, help='Use abacus or mentally.')
    abacus = style.add_argument('abacus', help='Calculate using an abacus.')
    mental = style.add_argument('mental', help='Calculate mentally.')
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
    arithmetic.add_argument('--path', type=str, default=None, help='Set the custom full file name of the created exercise (by default ./data/*.txt).')
    # create random [params] (name)
    ramdom.add_argument('params', type=str, help=help_params)
    random.add_argument('--path', type=str, default=None, help='Set the custom full file name of the created exercise (by default ./data/*.txt).')
    # create cover [params] (name)
    cover.add_argument('params', type=str, help=help_params)
    cover.add_argument('--path', type=str, default=None, help='Set the custom filename of the created exercise (by default ./data/*.txt).')
    # analyze [filiname]
    analyze.add_argument('path', type=str, help="Path to file.")
    # run <mode> [filiname]
    # run.add_argument('mode', type=str, help="")
    run.add_argument('path', type=str, help="Path to file.")
    # run-new <mode> arithmetic [first,diff,length] (name)
    # run-new <mode> random [params] (name)
    # run-new <mode> cover [params] (name)



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
