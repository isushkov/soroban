#!/usr/bin/env python3
import argparse
import sys
import src.helpers.exit_handler
from src.create import create
from src.analyze import analyze
from src.run import Run
from src.helpers.colors import *


def add_optarg_path(subparser):
    subparser.add_argument('--path', type=str, default=None, help='Set the custom full file name of the created exercise (by default ./data/*.txt).')
def add_arg_path(subparser):
    subparser.add_argument('path', type=str, help="Path to file.")
def add_args_style_mode(subparser):
    subparser.add_argument('style', choices=['abacus', 'mental'], help='Calculate using an abacus or mentally.')
    subparser.add_argument('mode', choices=['training', 'exam'], type=str, help="Training or exam.")
def add_arg_params(subparser):
    help_params =r"""params = "<start-number> <sequence> <sequence> ..."

  определяет характеристики выражения.
  должно быть указано минимум <start-number> и один <sequence>.

  <start-number>:
    начальное число в формате "sX", где X - любое число (влючая отрицательные и десятичные дроби),
    или "r" - сгенерировать рандомно из <range> и <decimal> из первого <sequence>.

  <sequence> = "<kind><seq_params>":
    <kind>:
      определяет "тип" последовательности:
        "a" - An arithmetic progression.
        "r" - Generate numbers randomly.
        "c" - Covering all possible combinations of the category of units.
    <seq_params>:
      параметры для <seq_params> состоят из двух секций: обязательные аргументы и необязательные.
      если указываются необязательных аргументы - они отделяются через двоеточие:

        <seq_params> = "<required>:<optional>"

      для <kind> = "a" :
        первым числом прогресси будет результат левой части выражения.
        <required>:
          обязательные параметры, отделяются друг от друга запятыми, указываются в строгом порядке:

            <required> = "<diff>,<length>"

          <diff>
            The difference between the numbers.
            любое число (влючая отрицательные и десятичные дроби), по умолчанию - нет.
          <length>
            The length of the progression.
            любое натуральное число, по умолчанию - нет.

        <optional>:
          необязательные параметры:

            <optional> = ":<roundtrip>"

          <roundtrip> = "<" (поумолчанию отлючено):
            добавить вконец копию инвертированной версии получившегося выражения:
              - отзеркалить последовательность чисел
              - преобразовать + в -, * в / и наоборот

      для <kind> = "r" or "c":
        <required>:
          обязательные параметры (кроме <lenght> для <kind>="c"), отделяются друг от друга запятыми,
          указываются в строгом порядке:

            <required> = "<operands>,<range>,<length>"

          <operands>:
            какие использовать операнды. варинаты: "+", "-", "*", "/".
            при указании нескольких операндов будут выбираться рандомно для каждого нового числа.
            после каждого операнда можно указать приоритет (любое натуральное число - по умолчанию "1").
          <range>:
            Диапазон для генерации чисел в виде "x-y", где "x" и "y" любые натуральные числа.
            Будет автоматически учтена точность знаков после запятой.
            Не может быть отрицательным - этот эфект достигается за счет операндов и их приоритетов.
          <lenght> (для kind=cover необятельный)
            длина последовательности, где <lenght> любое натуральное число.
            для kind=cover необзятельный, после того как все комбинации подобраны - генерировать числа рандомно.

        <optional>:
          необязательные параметры, друг от друга не отделяются, указываются в случайном порядке:

            <optional> = ":<allow-negative><decimal><roundtrip>"

          <allow-negative> = "n" (поумолчанию отлючено):
            если start-number >= 0 разрешить уходить в минус.
            если start-number  < 0 разрешить уходить меньше чем был start-number.
          <decimal> = ".x%%y" (поумолчанию отлючено):
            рандомно добавлять десятичные дроби с точностью до "x" знаков после запятой,
            где "x" любое натуральное число. поумолчанию - нет.
            в конце можно указать вероятность в процентах через "%%y",
            где "y" натуральное число от 0 до 100 (по умолчанию %%50).
          <roundtrip> = "<" (поумолчанию отлючено):
            добавить вконец копию инвертированной версии получившегося выражения:
              - отзеркалить последовательность чисел
              - преобразовать + в -, * в / и наоборот

примеры использования:
  "s0 a1,100",
  "s0 a1,100:<",
  "s5000 a-1,100",
  "s0 r+,1-99,100",
  "sr r+-,142-9345,5000",
  "s0 c+,1-9",
  "s0 c+,1-9,500",
  "s0 r+,1-9,50:<",
  "s0 r+,3-9,5:n",
  "s0 r+,3-9,5:n.2",
  "s0 r+,3-9,5:n.3%%10",
  "s0 r+,3-9,5:n.4%%100<",
  "s0 r+,3-99,100  r+-,142-9345,5000:n.3%%50 r+2-1,2-13,12:<",
  "s0 r+,3-99:<    r+-,1-999:n.2             r*2/,1-9,10"
"""
    subparser.add_argument('params', type=str, help=help_params)

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
    # run-new
    p_runnew = p_command.add_parser('run-new', help='Create, analyze and run a new exercise.')
    add_args_style_mode(p_runnew)
    add_arg_params(p_runnew)
    add_optarg_path(p_runnew)

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
