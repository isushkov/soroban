import re
import shutil
from collections import Counter
# src
from src.config import Config
import src.sequence as s
# src/view
from src.view.analyze import ViewAnalyze
# src/helpers
import src.helpers.fo as fo
import src.helpers.colors as c

view = ViewAnalyze()
def analyze(path):
    view.render_title(f'[y]ANALYZE {path}')
    config = Config()
    # exercise
    sequence, total_provided = fo.txt2str(path).split('=')
    sequence = s.validate_sequence(sequence, 'analyze sequence', exit_policy=2)
    operations = sequence.split()
    start_number = s.tonum(operations.pop(0))
    total_provided = validate_total(total)
    total = s.safe_eval(sequence)
    # density
    #   - посчитать количество знаков в самой длинной дробной чати.
    #   - умножить каждое число на 10^max_f, чтобы избавиться от дробей.
    #   - посчитать density.
    min_i, max_i, min_f, max_f = find_min_max_digits(sequence)
    density_pos, density_neg = get_density(start_number, operations, max_f)
    # data/render
    view.upd_total(get_data_total(density_pos, density_neg))
    view.upd_info(get_data_info(start_number, operations, max_f, total, total_provided), spoilers=config.spoilers)
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
def get_density(start_number, operations, max_f):
    density_pos = {}
    density_neg = {}
    total = start_number
    for operation in operations:
        operand, number_str = s.split_operation(operation)
        # TODO: * / *- /-
        if operand not in ['+', '-']: c.todo(f'density for "{operand}"')
        if operand == '+': density = density_pos
        if operand == '-': density = density_neg
        # сдвигаем число право на максимальное количество запятых
        # для каждого разряда. всего разрядов - длина второго слогаемого
        number = s.tonum(number_str) * (10 ** max_f)
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
def get_data_info(start_number, operations, max_f, total, total_provided):
    range_results = get_range_results(start_number, operations)
    return {
        'start_number': start_number,
        'ops_count': len(operations),
        'ops_operands': list(set(s.split_operation(op)[0] for op in operations)),
        'dec_exist': bool(max_f),
        'neg_exist': range_results[0] < 0 or False
        'range_numbers': get_range_numbers(operations),
        'range_results': range_results,
        'total_provided': total_provided,
        'total_correct': total == total_provided
    }
def get_range_numbers(operations):
    min_num, max_num = 0,0
    for op in operations:
        _, num = s.split_operation(op)
        if num < min_num: min_num = num
        if num > max_num: max_num = num
    return (min_num, max_num)
def get_range_results(start_number, operations):
    total, min_result, max_result = start_number, 0, 0
    for operation in operations:
        operand, num = s.split_operation(operation)
        total = s.do_math(total, operand, num)
        if total < min_result: min_result = total
        if total > max_result: max_result = total
    return (min_result, max_result)
