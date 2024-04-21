import random
import re
import sys
from collections import Counter
from src.helpers.fo import Fo as fo
from src.helpers.colors import *
from src.helper import *


def analyze(path):
    print(c_center(cz(f' [y]ANALYZE {path} '), 94, '=', 'x'))
    operations = parse_sequence(fo.txt2str(path))
    print(cz(f'[g]Lenght sequence:[c]  {len(operations)}'))
    max_shift, density_pos, density_neg = get_density(operations)
    # tables
    tables = []
    for shift in range(max_shift):
        tables.append(get_table(shift, density_pos.get(shift), density_neg.get(shift)))
    table_merged = merge_tables(tables)
    output_lenght = len(remove_colors(table_merged.split('\n')[0]))
    # table total
    density_total_pos = Counter()
    density_total_neg = Counter()
    for counter in density_pos.values():
        density_total_pos += counter
    for counter in density_neg.values():
        density_total_neg += counter
    table_total = align_table(get_table('total', density_total_pos, density_total_neg), output_lenght)
    # print
    print_header(output_lenght)
    print(table_merged)
    print(table_total)

def parse_sequence(sequence):
    expression, total = validate_sequence(re.sub(r'\s+', '', sequence)).split('=')
    total = dec(total)
    validate_total(total, expression)
    operations = re.findall(r'[\+\-\*/]?[\d\.]+', expression)
    operations = parse_operations(operations)
    operations = upd_first_operand(operations)
    operations = [(operator, dec(val)) for operator, val in operations]
    return operations
# TODO: разрешить без total
def validate_sequence(sequence):
    if not re.match(r'^\+?\d*\.?\d*(?:[+\-*/]\+?\d*\.?\d*)*=-?\d*\.?\d*$', sequence):
        print(cz('[r]FAIL:[c] Expression must be in [y]"num op num op ... = num"[c] format'))
        print(cz('      with [y]"+-/*"[c] operators and numbers can be [y]integer[c] or [y]float[c].'))
        exit(1)
    return sequence
def validate_total(total, expression):
    if dec(total) != safe_eval(expression):
        print(cz('[r]FAIL:[c] Mismatch between [y]provided total[c] and [y]calculated total[c].'))
        exit(1)
def parse_operations(operations):
    return [(op[0], op[1:]) if op[0] in '+-*/' else ('', op) for op in operations]
def upd_first_operand(operations):
    if operations[0][0] == '':
        operations[0] = ('+', operations[0][1])
    return operations

# combinations
def get_density(operations):
    max_shift = 0
    density_pos = {}
    density_neg = {}
    first_number = operations[0][1]
    # для каждой пары чисел
    for i,operation in enumerate(operations):
        if i == 0:
            continue
        operand = operations[i][0]
        second_number = operations[i][1]
        # для каждого разряда. всего разрядов - длина второго слогаемого
        second_number_lenght = len(str(second_number))
        if second_number_lenght > max_shift:
            max_shift = second_number_lenght
        for shift in range(second_number_lenght):
            if operand == '+':
                found = density_pos.get(shift, Counter())
                density_pos[shift] = upd_combs(shift, first_number, second_number, found)
            elif operand == '-':
                found = density_neg.get(shift, Counter())
                density_neg[shift] = upd_combs(shift, first_number, second_number, found)
            else:
                print(cz(f'[y]TODO:[c] operand "{operand}"'))
                exit(1)
        # next
        if operand == '+':
            first_number += second_number
        elif operand == '-':
            first_number -= second_number
        else:
            print(cz(f'[y]TODO:[c] operand "{operand}"'))
            exit(1)
    return max_shift, density_pos, density_neg
def upd_combs(shift, first_number, second_number, found):
    comb = get_digits(shift, first_number, second_number)
    found[comb] += 1 # сколько раз встретилась комбинация
    return found
def get_digits(shift, first_number, second_number):
    divisor = 10 ** shift
    digit_first  = (first_number // divisor) % 10
    digit_second = (second_number // divisor) % 10
    return digit_first, digit_second

# output
def merge_tables(tables):
    result = ''
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

def get_table(shift, density_pos, density_neg):
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
    # rows
    for y in range(9, -1, -1):
        row_middle = f' │ {y} │ '
        row_left   = get_density_row(y, density_neg, range(9, 0, -1))
        row_right  = get_density_row(y, density_pos, range(1, 10))
        table.append(cz('[x] │ [c]' + row_left + '[x]' + row_middle + '[c]' + row_right + '[x] │ '))
    # footer
    table.append(cz('[x] ├───────────┼───┼───────────┤ '))
    table.append(cz('[x] └─987654321─┘   └─123456789─┘ '))
    return table
def get_density_row(y, density, rng):
    row = ''
    for x in rng:
        count = density.get((y, x), 0) if density else 0
        row += get_count_str(count)
    return row
def get_count_str(count):
    if count == 0: return cz('[c] ')
    if count == 1: return cz('[g]x')
    if count <= 9: return cz(f'[y]{count}')
    if count > 9: return cz('[r]*')
    return str(count)
# output
def print_header(output_lenght):
    result  = '\n'
    result += c_center(cz('[x]COMBINATION DENSITY[c]'), output_lenght) + '\n'
    print(result)
