from src.helpers.colors import *
from src.helpers.fo import Fo as fo
from src.helpers.cmd import Cmd as cmd
from src.params import parse_params
from src.helper import *
import random
from decimal import Decimal


# common
def create(args):
    print(c_center(cz(f' [y]CREATING ({args.kind}) '), 94, '=', 'x'))
    if args.kind == 'arithmetic':
        return create_arithmetic(args.path, args.first, args.diff, args.length)
    params = parse_params(args.params, args.kind)
    if args.kind == 'random':
        return create_random(args.path, params)
    if args.kind == 'cover-units':
        return create_cover_units(args.path, params)
    print(cz(f'[r]unknown "kind" to create the exercise: {args.kind}'))
    exit(1)
def params2path(kind, params=False):
    if not params:
        return f'./data/{kind}.txt'
    name = f'./data/{kind}'
    for seq in params:
        start_number, operands, range_params, length = seq['required'].values()
        is_negative, is_roundtrip, float_params = seq['optional'].values()
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
    numbers = generate_arithmetic(first, diff, length)
    expression = get_arithmetic_expresion(numbers)
    total = num2str(sum(numbers, Decimal(0)))
    data = f'{expression} ={total}'
    # save
    path = path if path else params2path(f'arithmetic_{first}_{diff}_{length}')
    save_file(path, data)
    return path
def generate_arithmetic(first, diff, length):
    first = Decimal(str(first))
    diff = Decimal(str(diff))
    return [first + i * diff for i in range(length)]
def get_arithmetic_expresion(numbers):
    expression = ''
    for num in numbers:
        operand = '+' if num >= 0 else '-'
        if num == numbers[0]:
            pfx = ''
            if operand == '+':
                operand = ''
        else:
            pfx = ' '
        expression += f'{pfx}{operand}{num2str(abs(num))}'
    return expression

# random
def create_random(path, params):
    # data
    expression = ''
    is_first_seq = True
    for i,seq in enumerate(params):
        if i == 1: is_first_seq = False
        required = seq['required']
        optional = seq['optional']
        print(cz(f'[g]sequence_{i}:[c]'))
        print(cz(f'  [r]required:[c] {required}'))
        print(cz(f'  [y]optional:[c] {optional}'))
        sequence = create_random_sequence(required, optional, is_first_seq, safe_eval(expression))
        expression += sequence
    # save
    path = path if path else params2path('random', params)
    data = f'{expression} = {safe_eval(expression)}'
    expression
    save_file(path, data)
    return path
def create_random_sequence(required, optional, is_first_seq, total):
    start_number_param, operands, range_params, max_length = required.values()
    is_negative, is_roundtrip, float_params = optional.values()
    # start_number
    if is_first_seq:
        if start_number_param == 'r':
            start_number = create_random_number(range_params, float_params)
        else:
            start_number = num2str(start_number_param)
        total = Decimal(str(start_number))
        sequence = num2str(start_number)
    else:
        sequence = ''
    # sequence
    length = 1
    while length <= max_length:
        operand, number, total = create_operation(total, operands, range_params,
                                                  float_params, total, is_negative)
        sequence += ' ' + operand + num2str(number)
        length += 1
    # roundtrip
    if is_roundtrip:
        sequence += ' '
        elements = sequence.split()
        if is_first_seq:
            elements.pop(0)
        elements.reverse()
        reverse_sequence = ' '.join([switch_operand(el) for el in elements])
        sequence += reverse_sequence
    return sequence
def create_operation(start_number, operands, range_params, float_params, total, is_negative):
    backup = (start_number, operands, range_params, float_params, total, is_negative)
    operand = choose_operand(operands)
    number = Decimal(str(create_random_number(range_params, float_params)))
    total = do_math(operand, total, number)
    is_ok = True
    if not is_negative:
        if start_number >= 0 and total < 0:           is_ok = False
        if start_number < 0 and total < start_number: is_ok = False
        if len(operands) == 1 and operand == '-' and total - range_params[0] < 0:
            print(cz('[r]FAIL:[c] The sequence [r]was not created[c] due to conflicting parameters:'))
            print(cz('[y]FAIL:[c]   - Negative numbers are not allowed.'))
            print(cz('[y]FAIL:[c]   - Only "-" operands are used.'))
            print(cz('[y]FAIL:[c]   - The current result minus the minimum possible value is less than zero.'))
            print(cz('[y]FAIL:[c]   - The limit has been reached.'))
            exit(1)
    if not is_ok:
        operand, number, total = create_operation(*backup)
    return operand, number, total
def choose_operand(operands):
    operations, weights = zip(*operands.items())
    operand = random.choices(operations, weights=weights, k=1)[0]
    return operand
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

# cover-units
def create_cover(operations_kind, digits_range, name):
    print(c_center(cz(f' [y]CREATING (cover-units type) '), 94, '=', 'x'))
    print(cz(f'[g]operations_kind kind:[c] {operations_kind}[g], digits_range:[c] {digits_range}'))
    path = name2path(name) if name else name2path(f'cover-units_{operations_kind}_{digits_range}')
    # data
    numbers = get_cover_units(digits_range)
    if operations_kind == 'plus':
        total = sum(numbers)
        expression = get_expresion(numbers, operations_kind)
    if operations_kind == 'minus':
        numbers.append(sum(numbers))
        numbers.reverse()
        total = numbers.pop(-1)
        expression = get_expresion(numbers, operations_kind)
    # TODO: plus-minus
    if operations_kind == 'plus-minus':
        print(cz('[y]TODO:[c] cover-units plus-minus...'))
        exit(1)
    if operations_kind == 'plus-minus-roundtrip':
        expresion_plus = get_expresion(numbers, 'plus')
        numbers.reverse()
        total = numbers.pop(0)
        expresion_minus = get_expresion(numbers, 'minus')
        expression = f'{expresion_plus} - {expresion_minus}'
    # save
    data = f'{expression} ={total}'
    save_file(path, data)
    return path
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

# common
def get_expresion(numbers, operations_kind):
    if operations_kind == 'plus':
        return f' +'.join([str(i) for i in numbers])
    if operations_kind == 'minus':
        return f' -'.join([str(i) for i in numbers])
    # TODO: разрешить отрицательные
    if operations_kind == 'plus-minus':
        operators = ['+', '-']
        summ = numbers[0]
        expression = ''
        for num in numbers:
            if num == numbers[0]:
                continue
            choice = random.choice(operators)
            summ = summ + num if choice == '+' else summ - num
            if summ < 0:
                choice = '+'
                summ = summ + num
            expression += f' {choice}{num}'
        return expression
