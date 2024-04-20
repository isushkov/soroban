from src.helpers.colors import *
from src.helpers.fo import Fo as fo
from src.helpers.cmd import Cmd as cmd
from src.params import parse_params
from src.helper import *
import random


# common
def create(args):
    print(c_center(cz(f' [y]CREATING ({args.kind}) '), 94, '=', 'x'))
    if args.kind == 'arithmetic':
        path, data = create_arithmetic(args.path, args.first, args.diff, args.length)
    else:
        path, data = create_sequence(args.path, parse_params(args.params, args.kind), args.kind)
    save_file(path, data)
    return path
def params2path(kind, params=False):
    if not params:
        return f'./data/{kind}.txt'
    name = f'./data/{kind}'
    for seq_params in params:
        start_number, operands, range_params, length = seq_params['required'].values()
        is_negative, is_roundtrip, float_params = seq_params['optional'].values()
        precision = float_params['precision']
        probability = float_params['probability']
        m = {'+':'p', '-':'m', '*':'M', '/':'D'}
        start_number = str(start_number) if start_number else 'x'
        operands = ''.join([f'{m[k]}{v}' for k,v in operands.items()])
        range_params = 'x'.join(str(i) for i in range_params)
        length = length if length else 0
        float_params = f'dec{precision}x{probability}' if precision else 'dec0'
        negative = f'neg{1 if is_negative else 0}'
        roundtrip = f'rnd{1 if is_roundtrip else 0}'
        name += f'_{start_number}-{operands}-{range_params}-{length}_{float_params}-{negative}-{roundtrip}'
    name += '.txt'
    return name
def save_file(path, data):
    cmd.run('mkdir -p ./data')
    fo.str2txt(data, path)
    print(cz(f'[g]Exercise was created:[c] {path}'))
    print()

# arithmetic
def create_arithmetic(path, first, diff, length):
    print(cz(f'[g]first element:[c] {first}[g], diff: [c]{diff}, length: [c]{length}'))
    # data
    numbers = [dec(first) + i * dec(diff) for i in range(length)]
    sequence = ' '.join(f'{"+" if num >= 0 else "-"}{num2str(num)}' for num in numbers).lstrip('+')
    data = f'{sequence} ={num2str(safe_eval(sequence))}'
    path = path if path else params2path(f'arithmetic_{first}_{diff}_{length}')
    return path, data

# random/cover
def create_sequence(path, params, kind):
    # data
    expression = ''
    is_first_seq = True
    summ = dec(0)
    for i,seq_params in enumerate(params):
        if i == 1: is_first_seq = False
        print(cz(f'[g]sequence_{i}:[c]'))
        print(cz(f'  [r]required:[c] {seq_params["required"]}'))
        print(cz(f'  [y]optional:[c] {seq_params["optional"]}'))
        # start
        sequence_start, summ = create_sequence_start(is_first_seq, seq_params, summ)
        expression += sequence_start
        # random/cover
        if kind == 'random': sequence, summ = create_sequence_random(seq_params, summ)
        else:                sequence, summ = create_sequence_cover(seq_params, summ)
        expression += sequence
        # roundtrip
        if seq_params['optional']['roundtrip']:
            expression += create_sequence_roundtrip(sequence)
        check_sum(summ, expression)
    # save
    data = f'{expression} = {safe_eval(expression)}'
    path = path if path else params2path('random', params)
    return path, data
# random/cover sequences
def create_sequence_start(is_first_seq, seq_params, summ):
    if not is_first_seq:
        return '', summ
    if start_param != 'r':
        sequence = seq_params['required']['start_number']
    else:
        sequence = num2str(create_random_number(seq_params['required']['range'], seq_params['optional']['float']))
    return sequence, dec(sequence)
def create_sequence_roundtrip(sequence):
    elements = sequence.split()
    elements.reverse()
    return ' ' + ' '.join([switch_operand(el) for el in elements])
# random/cover common
def create_random_number(range_params, float_params):
    # должны ли мы генерировать float
    if float_params['precision']:
        # когда мы должны генерировать float
        if float_params['probability'] > random.randint(0, 100):
            number = random.uniform(*range_params)
            return format(number, f".{float_params['precision']}f")
        return random.randint(*range_params)
    return random.randint(*range_params)
def switch_operand(el):
    op_old = [op for op in '+-*/' if op in el][0]
    return el.replace(op_old, {'+':'-', '-':'+', '*':'/', '/':'*'}[op_old])
def check_sum(summ, expression):
    if summ != safe_eval(expression):
        print(cz(('[r]ERROR:[c] mismatch sums.'))
        exit(1)

# random
def create_sequence_random(seq_params, summ):
    _, operands, range_params, max_length = seq_params['required'].values()
    is_negative, _, float_params = seq_params['optional'].values()
    for _ in range(1, max_length + 1):
        operand, number, summ = create_operation_random(summ, operands, range_params, float_params, summ, is_negative)
        sequence += ' ' + operand + num2str(number)
    return sequence, summ
def create_operation_random(summ, operands, range_params, float_params, summ, is_negative):
    backup = (summ, operands, range_params, float_params, summ, is_negative)
    operand = choose_operand(operands)
    number = dec(create_random_number(range_params, float_params))
    summ = do_math(operand, summ, number)
    is_ok = True
    if not is_negative:
        if summ >= 0 and summ < 0:            is_ok = False
        if summ < 0  and summ < summ: is_ok = False
        if len(operands) == 1 and operand == '-' and summ - range_params[0] < 0:
            print(cz('[r]FAIL:[c] The sequence [r]was not created[c] due to conflicting parameters:'))
            print(cz('[y]FAIL:[c]   - Negative numbers are not allowed.'))
            print(cz('[y]FAIL:[c]   - Only "-" operands are used.'))
            print(cz('[y]FAIL:[c]   - The current result minus the minimum possible value is less than zero.'))
            print(cz('[y]FAIL:[c]   - The limit has been reached.'))
            exit(1)
    if not is_ok:
        operand, number, summ = create_operation_random(*backup)
    return operand, number, summ
def choose_operand(operands):
    operations, weights = zip(*operands.items())
    operand = random.choices(operations, weights=weights, k=1)[0]
    return operand

# cover
def create_sequence_cover(seq_params, summ):
    # _, operands, range_params, max_length = seq_params['required'].values()
    # is_negative, _, float_params = seq_params['optional'].values()
    # for _ in range(1, max_length + 1):
    #     operand, number, summ = create_operation_random(summ, operands, range_params, float_params, summ, is_negative)
    #     sequence += ' ' + operand + num2str(number)
    # return sequence, summ
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
