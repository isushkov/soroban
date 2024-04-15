import random
import re
import sys
from collections import Counter
from src.helpers.fo import Fo as fo
from src.helpers.colors import *


def analyze(path):
    print(c_center(cz(f' [y]ANALYZE {path} '), 94, '=', 'x'))
    numbers, chars = parse_sequence(fo.txt2str(path))
    print(cz(f'[g]Lenght sequence:[c]  {len(numbers)}'))
    founds = get_founds(numbers, chars)
    # output
    table_merged = merge_tables([get_table(found, shift, chars) for shift,found in founds.items()])
    found_total = Counter()
    for counter in founds.values():
        found_total += counter
    output_lenght = len(remove_colors(table_merged.split('\n')[0]))
    table_total = align_table(get_table(found_total, 'total', chars), output_lenght)
    # print
    print_header(output_lenght)
    print(table_merged)
    print(table_total)

# parse and validate
def parse_sequence(sequence):
    expression, total = validate_sequence(sequence).split('=')
    validate_total(str2num(total), eval(expression))
    numbers = list(map(str2num, re.findall(r'\d*\.?\d+', expression)))
    chars = ''.join(set(re.findall(r'[+\-*/]', expression)))
    filter_unsupported_chars(chars) # TODO
    return numbers, chars
def validate_sequence(sequence):
    sequence = re.sub(r'\s+', '', sequence)
    if not re.match(r'^(\d*\.?\d+[+\-*/])+\d*\.?\d+=\d*\.?\d+$', sequence):
        print(cz('[r]FAIL:[c] Expression must be in [y]"num op num op ... = num"[c] format'))
        print(cz('         with [y]"+-/*"[c] operations and numbers can be [y]integer[c] or [y]float[c].'))
    return sequence
def filter_unsupported_chars(chars):
    if len(chars) > 1:
        exit(cz(f'[y]TODO:[c] unsupported chars - "more than one type operations"'))
    unsupported_chars = ''.join([c for c in chars if c not in '+-'])
    if unsupported_chars:
        exit(cz(f'[y]TODO:[c] unsupported chars - "{unsupported_chars}"'))
def validate_total(total_provided, total_calculated):
    if total_provided != total_calculated:
        exit(cz('[r]FAIL:[c] Mismatch between [y]provided total[c] and [y]calculated total[c].'))
def str2num(s):
    s = float(s)
    return int(s) if s.is_integer() else s

# combinations
def get_founds(numbers, chars):
    founds = {}
    first_number = numbers[0]
    # для каждой пары чисел
    for i in range(len(numbers)):
        if i == 0: continue
        second_number = numbers[i]
        # для каждого разряда. всего разрядов - длина второго слогаемого
        for shift in range(len(str(second_number))):
            found = founds.get(shift, Counter())
            founds[shift] = upd_combs(shift, first_number, second_number, found)
        # next
        if chars == '+':
            first_number += second_number
        if chars == '-':
            first_number -= second_number
    return founds
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

def get_table(found, shift, chars):
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
    for y in range(9, -1, -1):
        row_middle = f' │ {y} │ '
        row_left  = (''.join([get_count_str(found.get((y, x), 0)) for x in range(9, 0, -1)])
                     if chars == '-' else (' '*9))
        row_right = (''.join([get_count_str(found.get((y, x), 0)) for x in range(1, 10)])
                     if chars == '+' else (' '*9))
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

def print_header(output_lenght):
    result  = '\n'
    result += c_center(cz('[x]COMBINATION DENSITY[c]'), output_lenght) + '\n'
    print(result)
