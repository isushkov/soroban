import random
import re
from collections import Counter
from src.helpers.fo import Fo as fo
from src.helpers.colors import *
from src.helpers.fexit import fexit


def analyze(exercise):
    numbers_part, total_part = fo.txt2str(f'data/{exercise}.txt').split('=')
    numbers = [int(num) for num in re.findall(r'\d+', numbers_part)]
    first_number = numbers[0]
    operation = get_operation(numbers_part)
    total = get_total(numbers, operation, int(total_part.strip()))
    # info
    print(c_center(cz(f' [y]ANALYZE {exercise} '), 94, '=', 'x'))
    print(cz(f'[g]Lenght sequence:[c]  {len(numbers)}'))
    print(cz(f'[g]Calculated total:[c] {total}'))
    print(cz(f'[g]Provided total:[c]   {total}'))
    print(cz( '[g]OK:[c] The calculated total matches the provided total.'))
    # run
    founds = {}
    remains = {}
    combs_all = {(i, j) for i in range(0, 10) for j in range(1, 10)}
    # для каждой пары чисел
    for i in range(len(numbers)):
        if i == 0: continue
        second_number = numbers[i]
        # для каждого разряда. всего разрядов - длина второго слогаемого
        for shift in range(len(str(second_number))):
            found = founds.get(shift, Counter())
            remain = remains.get(shift, combs_all)
            founds[shift], remains[shift] = upd_combs(shift, first_number, second_number, found, remain, operation)
        # next
        first_number += second_number
    # output for digits
    tables = []
    for shift,found in founds.items():
        tables.append(get_table(found,shift))
    merged = merge_tables(tables)
    output_lenght = len(remove_colors(merged.split('\n')[0]))
    # output for total
    found_total = Counter()
    for counter in founds.values():
        found_total += counter
    table_total = get_table(found_total, 'total')
    total = align_table(table_total, output_lenght)
    # print
    print_header(output_lenght)
    print(merged)
    print(total)

# input
def get_operation(numbers_part):
    operation_chars = re.findall(r'\s([+\-*/])\s', numbers_part)
    operation = operation_chars[0] if operation_chars else None
    if not operation:
        fexit('operation not defined')
    return operation
def get_total(numbers, operation, total_provided):
    if operation == '+':
        total_calculated = sum(numbers)
    elif operation == '-':
        first_number = numbers.pop(0)
        total_calculated = first_number - sum(numbers)
    else:
        fexit(f'TODO: unknown operation ({operation})')
    if total_calculated != total_provided:
        fexit(cz('[r]FAIL:[c] Mismatch between [y]calculated total[c] and [y]provided total[c].'))
    return total_calculated

# combinations
def upd_combs(shift, first_number, second_number, found, remain, operation):
    comb = get_digits(shift, first_number, second_number, operation)
    found[comb] += 1 # сколько раз встретилась комбинация
    if comb in remain:
        remain.discard(comb)
    return found, remain
def get_digits(shift, first_number, second_number, operation):
    divisor = 10 ** shift
    digit_first  = (first_number // divisor) % 10
    digit_second = (second_number // divisor) % 10
    return digit_first, digit_second

# output
def merge_tables(tables):
    result = ''
    # определяем количество строк
    num_lines = len(tables[0]) if tables else 0
    # проходим по группам по три таблицы
    for g in range(0, len(tables), 3):
        group = tables[g:g+3]  # получаем текущую группу из максимум трёх таблиц
        for i in range(num_lines):
            merged_line = ''.join(table[i] for table in group)
            result += '  ' + merged_line + '\n'
    return result
def align_table(table, output_lenght):
    result = ''
    for line in table:
        result += ' ' + c_center(line, output_lenght) + '\n'
    return result
def print_header(output_lenght):
    result  = '\n'
    result += c_center(cz('[x]COMBINATION DENSITY[c]'), output_lenght) + '\n'
    print(result)
def get_table(found, shift):
    table = []
    # title
    shift2title = {
      'total': '──[ TOTAL ]──',
        0:     '──[ Units ]──',
        1:     '──[ Tens ]───',
        2:     '─[ Hundreds ]',
    }
    title = shift2title.get(shift, f'──[ 10 ^{shift} ]──')
    table.append(cz(f'[x]     ┌───{title}───┐     '))
    table.append(cz( '[x] ┌───┴─[ - ]─┬───┬─[ + ]─┴───┐ '))
    # rows
    for x in range(9, -1, -1):  # От 9 до 0 включительно
        row_left = '         '
        row_middle = f' │ {x} │ '
        # right
        row_right = ''
        for y in range(1, 10):
            count = found.get((x, y), 0)
            row_right += get_count_str(count)
        # apply
        table.append(cz('[x] │ [c]' + row_left + '[x]' + row_middle + '[c]' + row_right + '[x] │ '))
    # footer
    table.append(cz('[x] ├───────────┼───┼───────────┤ '))
    table.append(cz('[x] └─987654321─┘   └─123456789─┘ '))
    return table
def get_count_str(count):
    if count == 0: return cz('[c] ')
    if count == 1: return cz('[g]x')
    if count <= 9: return cz(f'[y]{count}')
    if count > 9: return cz('[r]*')
    return str(count)
