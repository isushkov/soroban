import re
from collections import Counter
import src.helper as h
import src.helpers.colors as c
from src.helpers.fo import Fo as fo

# validation.
# density:
#   найти самую длинную дробную чать, посчитать количество знаков.
#   умножить каждое число на 10^max_f, чтобы избавиться от дробей.
#   посчитать density.
# render:
#   сместить названия таблиц на 10^(-max_fract_digits).
def analyze(path):
    print(c.center(c.z(f' [y]ANALYZE {path} '), 94, '=', 'x'))
    # validation
    sequence, total = fo.txt2str(path).split('=')
    sequence = h.validate_sequence(sequence, 'analyze sequence', exit_policy=2)
    total_is_valid = validate_total(total)
    # density
    min_i, min_f, max_i, max_f = find_min_max_digits(sequence)
    density_pos, density_neg = get_density(sequence, max_f)
    # render

    # TODO: не по три а на всю ширину, выранвнивая по левому краю
    # TODO: сепаратор
    # digits
    tables = []
    for d in range(max_i + max_f):
        tables.append(get_table(d, density_pos.get(d), density_neg.get(d)))
    table_merged = merge_tables(tables)
    output_lenght = len(c.remove_colors(table_merged.split('\n')[0]))
    # total
    density_total_pos = Counter()
    density_total_neg = Counter()
    for counter in density_pos.values():
        density_total_pos += counter
    for counter in density_neg.values():
        density_total_neg += counter
    table_total = align_table(get_table('total', density_total_pos, density_total_neg), output_lenght)
    print_header(output_lenght)
    print(table_merged)
    print(table_total)
    # info
    info = {
        'start_number': sequence.split()[0],
        'count_numbers': len(sequence.split()),
        'existed_operands': ' '.join(list(set(h.split_operation(op)[0] for op in sequence.split()))),
        'range_digits': render_range(min_i,min_f,max_i,max_f),
        'decimal_exist': render_yn(max_f),
        # 'decimal_precision': calc_decimal_precision(operations),
        # 'negative_results_exist': render_yn(calc_negative_results(operations)),
        'total_provided': render_yn(total),
        'total_valid': render_yn(total_is_valid),
        'total_correct': render_yn(check_total(total, sequence))
    }
    print(info)

# validate
def validate_total(total):
    total = h.validate_sequence(total, 'analyze total', exit_policy=1)
    msg = c.z(f'[y]NOTE:[c] total is invalid - [r]"{total}"')
    if not total:
        print(msg); return False
    if not bool(re.match(r'^-?\d+(\.\d+)?$', total)):
        print(msg); return False
    return False
# density
def find_min_max_digits(sequence):
    numbers = re.findall(r'[+\-*/]?(\d+(\.\d+)?)', sequence)
    min_i, min_f, max_i, max_f = float('inf'), float('inf'), 0, 0
    for number, decimal_part in numbers:
        if '.' in number:
            integ_part, fract_part = number.split('.')
            min_f = min(min_f, len(fract_part))
            max_f = max(max_f, len(fract_part))
        else:
            integ_part = number
        min_i = min(min_i, len(integ_part))
        max_i = max(max_i, len(integ_part))
    if min_f == float('inf'): min_f = 0
    if min_f == float('inf'): min_i = 0
    return min_i, min_f, max_i, max_f
def get_density(sequence, max_f):
    density_pos = {}
    density_neg = {}
    operations = sequence.split()
    # для каждой пары чисел
    total = h.dec(operations[0])
    for operation in operations[1:]:
        operand, number_str = h.split_operation(operation)
        # TODO: * / *- /-
        if operand not in ['+', '-']:
            print(c.z(f'[y]TODO:[c] calculate density for operand "{operand}"'))
            exit(2)
        # сдвигаем число право на максимальное количество запятых
        number = h.dec(number_str) * (10 ** max_f)
        if operand == '+': density = density_pos
        if operand == '-': density = density_neg
        # для каждого разряда. всего разрядов - длина второго слогаемого
        for d in range(len(str(number))):
            d_density = density.get(d, Counter())
            density[d] = upd_density(d_density, d, total, number)
        # next
        if operand == '+': density_pos = density
        if operand == '-': density_neg = density
        total = h.do_math(total, operand, number)
    return density_pos, density_neg
def upd_density(d_density, d, total, number):
    y,x = get_yx(total, number, d)
    d_density[(y,x)] += 1 # сколько раз встретилась комбинация
    return d_density
def get_yx(total, number, d):
    divisor = 10 ** d
    y = (total // divisor) % 10
    x = (number // divisor) % 10
    return y,x

# render
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
        result += ' ' + c.center(line, output_lenght) + '\n'
    return result
def get_table(d, density_pos, density_neg):
    table = []
    # title
    shift2title = {
      'total': '──[ TOTAL ]──',
        0:     '──[ Units ]──',
        1:     '──[ Tens ]───',
        2:     '─[ Hundreds ]',
    }
    title = shift2title.get(d, f'──[ 10 ^{d} ]──')
    table.append(c.z(f'[x]     ┌───{title}───┐     '))
    table.append(c.z( '[x] ┌───┴─[ - ]─┬───┬─[ + ]─┴───┐ '))
    # rows
    for y in range(9, -1, -1):
        row_middle = f' │ {y} │ '
        row_left   = get_density_row(y, density_neg, range(9, 0, -1))
        row_right  = get_density_row(y, density_pos, range(1, 10))
        table.append(c.z('[x] │ [c]' + row_left + '[x]' + row_middle + '[c]' + row_right + '[x] │ '))
    # footer
    table.append(c.z('[x] ├───────────┼───┼───────────┤ '))
    table.append(c.z('[x] └─987654321─┘   └─123456789─┘ '))
    return table
def get_density_row(y, density, rng):
    row = ''
    for x in rng:
        count = density.get((y, x), 0) if density else 0
        row += get_count_str(count)
    return row
def get_count_str(count):
    if count == 0: return c.z('[c] ')
    if count == 1: return c.z('[g]x')
    if count <= 9: return c.z(f'[y]{count}')
    if count > 9: return c.z('[r]*')
    return str(count)
def print_header(output_lenght):
    result  = '\n'
    result += c.center(c.z('[x]COMBINATION DENSITY[c]'), output_lenght) + '\n'
    print(result)
def render_yn(val):
    return c.z(f'[g]{"YES" if val else "NO"}')
def check_total(total, sequence):
    return True if h.dec(total) == h.safe_eval(sequence) else False
def render_range(min_i,min_f,max_i,max_f):
    d_min = '.' if min_f else ''
    d_max = '.' if max_f else ''
    return c.z(f"{'x'*min_i}{d_min}{'x'*min_f}[x]-[c]{'x'*max_i}{d_max}{'x'*max_f}")
