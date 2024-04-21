from src.helpers.colors import *
from src.helpers.fo import Fo as fo
from src.helpers.cmd import Cmd as cmd
from src.params import parse_params
from src.helper import *
import random


# init
def create(args):
    print(c_center(cz(f' [y]CREATING '), 94, '=', 'x'))
    params = parse_params(args.params)
    expression = ''
    # start
    start_param = params.pop(0)
    sequence, total = create_sequence_start(start_param, params[0])
    expression += sequence
    # sequence
    fnames = []
    for i,seq_params in enumerate(params):
        kind = seq_params['kind']
        print(cz(f'[g]sequence {i}. [y]{render_kind(kind)}:'))
        print(cz(f'  [r]required:[c] {render_dict(seq_params["required"])}'))
        print(cz(f'  [y]optional:[c] {render_dict(seq_params["optional"])}'))
        is_roundtrip = seq_params['optional']['roundtrip']
        # arithmetic
        if kind == 'a':
            first = safe_eval(expression)
            diff, length = seq_params['required'].values()
            sequence, total = create_sequence_arithmetic(first, diff, length, total)
            # append
            expression += sequence
            fnames.append(f'{render_kind(kind)}_{first}_{diff}_{length}_rnd{int(is_roundtrip)}')
        # random/cover
        elif kind in ['r', 'c']:
            # random/cover
            if kind == 'r': sequence, total = create_sequence_random(seq_params, total)
            else:           sequence, total = create_sequence_cover(seq_params, total)
            # append
            expression += sequence
            fnames.append(seq_params2part_name(seq_params))
        else:
            print(cz(f'[r]ERROR:[c] unknown kind - "{kind}".'))
            exit(2)
        # roundtrip
        if is_roundtrip:
            sequence, total = create_sequence_roundtrip(sequence, total)
            # append
            expression += sequence
        check_total(total, expression)
    # save
    data = f'{expression} = {safe_eval(expression)}'
    path = args.path if args.path else f'./data/{start_param}__{"__".join(fnames)}.txt'
    save_file(path, data)
    return path

# sequences/start.roundtrip.arithmetic
def create_sequence_start(start_param, seq_params):
    if start_param != 'r':
        return start_param, safe_eval(start_param)
    sequence = num2str(create_random_number(seq_params['required']['range'], seq_params['optional']['float']))
    return sequence, safe_eval(sequence)
def create_sequence_roundtrip(sequence, total):
    elements = sequence.split()
    elements.reverse()
    sequence = ' ' + ' '.join([switch_operand(el) for el in elements])
    total = total + safe_eval(sequence)
    return sequence, total
def create_sequence_arithmetic(first, diff, length, total):
    numbers = [dec(first) + i * dec(diff) for i in range(int(length))]
    sequence = ' ' + ' '.join(f'{"+" if num >= 0 else "-"}{num2str(num)}' for num in numbers)
    total = total + safe_eval(sequence)
    return sequence, total

# sequences/random
def create_sequence_random(seq_params, total):
    operands, range_params, length_param = seq_params['required'].values()
    is_negative, decimal_params, _ = seq_params['optional'].values()
    sequence = ''
    for _ in range(1, int(length_param) + 1):
        operand, number, total = create_operation_random(operands, range_params, decimal_params, is_negative, total)
        sequence += ' ' + operand + num2str(number)
    return sequence, total
def create_operation_random(operands, range_params, decimal_params, is_negative, total):
    backup = (operands, range_params, decimal_params, is_negative, total)
    operand = choose_operand(operands)
    number = dec(create_random_number(range_params, decimal_params))
    total = do_math(operand, total, number)
    is_ok = True
    if not is_negative:
        if total >= 0 and total < 0:            is_ok = False
        if total < 0  and total < total: is_ok = False
        if len(operands) == 1 and operand == '-' and total - dec(range_params[0]) < 0:
            print(cz('[r]FAIL:[c] The sequence [r]was not created[c] due to conflicting parameters:'))
            print(cz('[y]FAIL:[c]   - Negative numbers are not allowed.'))
            print(cz('[y]FAIL:[c]   - Only "-" operands are used.'))
            print(cz('[y]FAIL:[c]   - The current result minus the minimum possible value is less than zero.'))
            print(cz('[y]FAIL:[c]   - The limit has been reached.'))
            exit(1)
    if not is_ok:
        operand, number, total = create_operation_random(*backup)
    return operand, number, total
def choose_operand(operands):
    operations, weights = zip(*operands.items())
    operand = random.choices(operations, weights=weights, k=1)[0]
    return operand

# sequences/cover
def create_sequence_cover(seq_params, total):
    print(cz('[y]>>>>>>>> TODO'))
    exit(1)
    # _, operands, range_params, length_param = seq_params['required'].values()
    # is_negative, _, decimal_params = seq_params['optional'].values()
    # for _ in range(1, length_param + 1):
    #     operand, number, total = create_operation_random(operands, range_params, decimal_params, is_negative, total)
    #     sequence += ' ' + operand + num2str(number)
    # return sequence, total
    numbers = get_cover_units(digits_range)
def get_cover_units(digits_range):
    first_number = 0
    result = [first_number]
    all_combinations = {(x, y) for x in range(0, 10) for y in range(1, 10)}
    while all_combinations:
        x,y, all_combinations = get_units(first_number, all_combinations)
        second_number = generate_second_number(digits_range, y)
        result.append(second_number)
        first_number += second_number
    return result
def get_units(first_number, all_combinations):
    x = first_number % 10
    x_pairs = [(i, y) for i, y in all_combinations if i == x]
    if x_pairs:
        xy_pair = random.choice(list(x_pairs))
        all_combinations.remove(xy_pair)
        y = xy_pair[1]
    else:
        y = random.randint(1, 9)
    return x,y, all_combinations
def generate_second_number(digits_range, y):
    start, end = get_range(digits_range)
    random_number = random.randint(start, end)
    return (random_number // 10) * 10 + y

# sequences/random.cover - common
def create_random_number(range_params, decimal_params):
    range_values = (int(i) for i in range_params)
    # должны ли мы генерировать float
    if decimal_params['precision']:
        # когда мы должны генерировать float
        if int(decimal_params['probability']) > random.randint(0, 100):
            number = random.uniform(*range_values)
            return dec(format(number, f".{decimal_params['precision']}f"))
        return dec(random.randint(*range_values))
    return dec(random.randint(*range_values))
def switch_operand(el):
    op_old = [op for op in '+-*/' if op in el][0]
    return el.replace(op_old, {'+':'-', '-':'+', '*':'/', '/':'*'}[op_old])
def check_total(total, expression):
    if total != safe_eval(expression):
        print(cz('[r]ERROR:[c] mismatch totals.'))
        exit(1)

# common
def render_kind(kind):
    return {'a':'arithm', 'r':'random', 'c':'cover'}[kind]
def render_dict(data):
    return cz(f'{" ".join([f"[x]{k}=[c]{v}" for k,v in data.items()])}')

def seq_params2part_name(seq_params):
    operands, range_params, length = seq_params['required'].values()
    is_negative, decimal_params, is_roundtrip = seq_params['optional'].values()
    precision = decimal_params['precision']
    probability = decimal_params['probability']
    m = {'+':'p', '-':'m', '*':'M', '/':'D'}
    operands = ''.join([f'{m[k]}{v}' for k,v in operands.items()])
    range_params = 'x'.join(str(i) for i in range_params)
    length = length if length else 0
    decimal_params = f'dec{precision}x{probability}' if precision else 'dec0'
    negative = f'neg{1 if is_negative else 0}'
    roundtrip = f'rnd{1 if is_roundtrip else 0}'
    return f'{operands}_{range_params}_{length}_{negative}_{decimal_params}_{roundtrip}'
def save_file(path, data):
    cmd.run('mkdir -p ./data')
    fo.str2txt(data, path)
    print(cz(f'[g]Exercise was created:[c] {path}'))
    print()
