import re
import shutil
from collections import Counter
# src
import src.sequence as s
# src/view
from src.view.analyze import ViewAnalyze
# src/helpers
import src.helpers.fo as fo
import src.helpers.colors as c

view = ViewAnalyze()
def analyze(path):
    view.render_title(f'[y]ANALYZE {path}')
    # validation
    sequence, total = fo.txt2str(path).split('=')
    sequence = s.validate_sequence(sequence, 'analyze sequence', exit_policy=2)
    total_is_valid = validate_total(total)
    # density
    #   - посчитать количество знаков в самой длинной дробной чати.
    #   - умножить каждое число на 10^max_f, чтобы избавиться от дробей.
    #   - посчитать density.
    min_i, max_i, min_f, max_f = find_min_max_digits(sequence)
    density_pos, density_neg = get_density(sequence, max_f)
    # data/render
    view.upd_total(get_data_total(density_pos, density_neg))
    view.upd_info(get_data_info(sequence, min_i,max_i,min_f,max_f, total, total_is_valid) spoilers=False)
    view.upd_sepline()
    view.render_header()
    view.render_decim(density2data(max_f, density_pos, density_neg))
    if view.decim: view.display_sepline()
    view.render_integ(density2data(max_i, density_pos, density_neg))
    if view.decim: view.display_sepline()
    view.render_totalinfo()

# validate
def validate_total(total):
    total = s.validate_sequence(total, 'analyze total', exit_policy=1)
    msg = c.z(f"[y]NOTE:[c] total is invalid - [r]'{total}'")
    if not total:
        print(msg); return False
    if not bool(re.match(r'^-?\d+(\.\d+)?$', total)):
        print(msg); return False
    return True

# density
def find_min_max_digits(sequence):
    numbers = re.findall(r'[+\-*/]?(\d+(\.\d+)?)', sequence)
    min_i, min_f, max_i, max_f = float('inf'), float('inf'), 0, 0
    for number, decimal_part in numbers:
        if '.' in number:
            integ_part, decim_part = number.split('.')
            min_f = min(min_f, len(decim_part))
            max_f = max(max_f, len(decim_part))
        else:
            integ_part = number
        min_i = min(min_i, len(integ_part))
        max_i = max(max_i, len(integ_part))
    if min_f == float('inf'): min_f = 0
    if min_f == float('inf'): min_i = 0
    return min_i, max_i, min_f, max_f
def get_density(sequence, max_f):
    density_pos = {}
    density_neg = {}
    operations = sequence.split()
    # для каждой пары чисел
    total = s.tonum(operations[0])
    for operation in operations[1:]:
        operand, number_str = s.split_operation(operation)
        # TODO: * / *- /-
        if operand not in ['+', '-']: c.todo(f'density for "{operand}"')
        # сдвигаем число право на максимальное количество запятых
        number = s.tonum(number_str) * (10 ** max_f)
        if operand == '+': density = density_pos
        if operand == '-': density = density_neg
        # для каждого разряда. всего разрядов - длина второго слогаемого
        for digit in range(len(str(number))):
            d_density = density.get(digit, Counter())
            density[digit] = upd_density(d_density, digit, total, number)
        # next
        if operand == '+': density_pos = density
        if operand == '-': density_neg = density
        total = s.do_math(total, operand, number)
    return density_pos, density_neg
def upd_density(d_density, digit, total, number):
    y,x = get_yx(total, number, digit)
    d_density[(y,x)] += 1 # сколько раз встретилась комбинация
    return d_density
def get_yx(total, number, digit):
    divisor = 10 ** digit
    y = (total // divisor) % 10
    x = (number // divisor) % 10
    return y,x

# data.density
def density2data(max_d, density_pos, density_neg):
    data = {}
    for digit in range(0, max_d):
        data[digit] = {}
        data[digit]['pos'] = digit_density2data(density_pos.get(digit))
        data[digit]['neg'] = digit_density2data(density_neg.get(digit))
    return data
def get_data_total(density_pos, density_neg):
    density_total_pos = Counter()
    density_total_neg = Counter()
    for counter in density_pos.values():
        density_total_pos += counter
    for counter in density_neg.values():
        density_total_neg += counter
    data['total']['pos'] = digit_density2data(density_total_pos)
    data['total']['neg'] = digit_density2data(density_total_neg)
    return data_total
def digit_density2data(density):
    data_digit = {}
    for y in range(9, -1, -1):
        data_digit[y]['pos'] = y_density2data(y, density_neg, range(9, 0, -1))
        data_digit[y]['neg'] = y_density2data(y, density_pos, range(1, 10))
    return data_digit
def y_density2data(y, density, rng):
    row = ''
    for x in rng:
        count = density.get((y, x), 0) if density else 0
        row += str(count if count < 9 else 'm')
    return row
# data.info
def get_data_info(sequence, min_i,max_i,min_f,max_f, total, total_is_valid):
    operations = sequence.split()
    start_number = operations.pop(0)
    ops_operands = ' '.join(list(set(s.split_operation(op)[0] for op in sequence.split()))).strip()
    d_min = '.' if min_f else ''
    d_max = '.' if max_f else ''
    range_numbers = f"{'x'*min_i}{d_min}{'x'*min_f}-{'x'*max_i}{d_max}{'x'*max_f}"
    return {
        'start_number': start_number,
        'ops_count': len(operations),
        'ops_operands': ops_operands,
        'dec_exist': bool(max_f),
        'neg_exist': s.apply(lambda total: total < 0, sequence),
        'range_numbers': range_numbers,
        'range_results': s.apply(get_range_results, sequence),
        'total_provided': total,
        'total_valid': total_is_valid,
        'total_correct': s.tonum(total) == s.safe_eval(sequence)
    }
def get_range_results(total, range_results=(0,0)):
    min_result, max_result = range_results
    if total < min_result: min_result = total
    if total > max_result: max_result = total
    return (min_result, max_result)
