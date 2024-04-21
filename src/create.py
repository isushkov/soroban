import random
from src.params import parse_params
import src.helper as h
import src.helpers.colors as c
from src.helpers.fo import Fo as fo
from src.helpers.cmd import Cmd as cmd

# init
def create(args):
    print(c.center(c.z(f' [y]CREATING '), 94, '=', 'x'))
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
        print(c.z(f'[g]sequence {i} ({render_kind(kind)}):'))
        print(c.z(f'  [g]required:[c] {seq_params["required"]}'))
        print(c.z(f'  [g]optional:[c] {seq_params["optional"]}'))
        is_roundtrip = seq_params['optional']['roundtrip']
        # arithmetic
        if kind == 'a':
            first = h.safe_eval(expression)
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
            print(c.z(f'[r]ERROR:[c] unknown kind - "{kind}".'))
            exit(2)
        # roundtrip
        if is_roundtrip:
            sequence, total = create_sequence_roundtrip(sequence, total)
            # append
            expression += sequence
        check_total(total, expression)
    # save
    data = f'{expression} = {h.safe_eval(expression)}'
    path = args.path if args.path else f'./data/x{start_param}__{"__".join(fnames)}.txt'
    save_file(path, data)
    return path
# common
def render_kind(kind):
    return {'a':'arithm', 'r':'random', 'c':'cover'}[kind]
def render_dict(data):
    return c.z(f'{" ".join([f"[x]{k}=[c]{v}" for k,v in data.items()])}')
def check_total(total, expression):
    if total != h.safe_eval(expression):
        print(c.z('[r]ERROR:[c] mismatch totals.'))
        exit(1)
def seq_params2part_name(seq_params):
    operands, range_params, length = seq_params['required'].values()
    negative_allowed, decimal_params, is_roundtrip = seq_params['optional'].values()
    precision = decimal_params['precision']
    probability = decimal_params['probability']
    m = {'+':'p', '-':'m', '*':'M', '/':'D'}
    operands = ''.join([f'{m[k]}{v}' for k,v in operands.items()])
    range_params = 'x'.join(str(i) for i in range_params)
    length = length if length else 0
    decimal_params = f'dec{precision}x{probability}' if precision else 'dec0'
    negative = f'neg{1 if negative_allowed else 0}'
    roundtrip = f'rnd{1 if is_roundtrip else 0}'
    return f'{operands}_{range_params}_{length}_{negative}_{decimal_params}_{roundtrip}'
def save_file(path, data):
    cmd.run('mkdir -p ./data')
    fo.str2txt(data, path)
    print(c.z(f'[g]Exercise was created:[c] {path}'))
    print()

# sequence/start.roundtrip.arithmetic
def create_sequence_start(start_param, seq_params):
    if start_param != 'r':
        return start_param, h.safe_eval(start_param)
    sequence = h.num2str(create_random_number(seq_params['required']['range'], seq_params['optional']['float']))
    return sequence, h.safe_eval(sequence)
def create_sequence_roundtrip(sequence, total):
    elements = sequence.split()
    elements.reverse()
    sequence = ' ' + ' '.join([switch_operand(el) for el in elements])
    total = total + h.safe_eval(sequence)
    return sequence, total
def switch_operand(el):
    op_old = [op for op in '+-*/' if op in el][0]
    return el.replace(op_old, {'+':'-', '-':'+', '*':'/', '/':'*'}[op_old])
def create_sequence_arithmetic(first, diff, length, total):
    numbers = [h.dec(first) + i * h.dec(diff) for i in range(int(length))]
    sequence = ' ' + ' '.join(f'{"+" if num >= 0 else "-"}{h.num2str(num)}' for num in numbers)
    total = total + h.safe_eval(sequence)
    return sequence, total

# sequence/random
def create_sequence_random(seq_params, total):
    operands, range_params, length_param = seq_params['required'].values()
    negative_allowed, decimal_params, _ = seq_params['optional'].values()
    sequence = ''
    for _ in range(1, int(length_param) + 1):
        operand, number, total = create_operation_random(operands, range_params, decimal_params, negative_allowed, total)
        sequence += ' ' + operand + h.num2str(number)
    return sequence, total
def create_operation_random(operands, range_params, decimal_params, negative_allowed, total):
    backup = (operands, range_params, decimal_params, negative_allowed, total)
    operand = choose_operand(operands)
    number = h.dec(create_random_number(range_params, decimal_params))
    total = h.do_math(total, operand, number)
    if not check_operation_by_negative_effects(negative_allowed, 'r', total, operands, range_params[0]):
        operand, number, total = create_operation_random(*backup)
    return operand, number, total
# sequence/cover
def create_sequence_cover(seq_params, total):
    operands, range_params, length_param = seq_params['required'].values()
    negative_allowed, decimal_params, _ = seq_params['optional'].values()
    # TODO: cover-units decimal
    if decimal_params['precision']:
        print(c.z('[y]TODO:[c] cover-units for decimal'))
        exit(2)
    # TODO: cover-units for "*/"
    if '*' in operands or '/' in operands:
        print(c.z('[y]TODO:[c] cover-units for */'))
        exit(2)
    # TODO: cover-units for "negative_allowed"
    if negative_allowed:
        print(c.z('[y]TODO[c]: cover-units for negative_allowed'))
        exit(2)
    sequence = ''
    combs = {(x, y) for x in range(0, 10) for y in range(1, 10)}
    combs_pos = combs if '+' in operands else {}
    combs_neg = combs if '-' in operands else {}
    while combs_pos and combs_neg:
        operand, number, total, combs_pos, combs_pos = create_operation_cover(
            operands, range_params, decimal_params, negative_allowed, total, combs_pos, combs_neg)
        sequence += ' ' + operand + h.num2str(number)
    # если был указан length_param, после того как все комбинации подобраны генерировать числа рандомно.
    is_noticed = False
    while int(length_param) > len(numbers):
        if not is_noticed:
            print(c.z(f'[y]NOTE:[g] All combinations were matched:'))
            print(c.z(f'[y]NOTE:[c]   the current length is [y]{len(numbers)}.'))
            print(c.z(f'[y]NOTE:[c]   the specified length in the parameters is {length_param}.'))
            print(c.z(f'[y]NOTE:[c] The rest of the sequence will be generated randomly.'))
            is_noticed = True
        operand, number, total = create_operation_random(operands, range_params, decimal_params, negative_allowed, total)
        sequence += ' ' + operand + h.num2str(number)
    return sequence, total
def create_operation_cover(operands, range_params, decimal_params, negative_allowed, total):
    backup = (operands, range_params, decimal_params, negative_allowed, total, combs_pos, combs_neg)
    if not negative_allowed and total < 0:
        print(c.z('[y]TODO:[c] cover-units for negative'))
        exit(2)
    operand = choose_operand(operands)
    if operand not in ['+', '-']:
        print(c.z('[y]TODO:[c] cover-units for */'))
        exit(2)
    x = total % 10
    if operand == '+': y, combs_pos = extract_random_y_from_combs(combs_pos, x)
    if operand == '-': y, combs_neg = extract_random_y_from_combs(combs_neg, x)
    number = h.dec(create_random_number(range_params, decimal_params))
    if y: number = replace_units(number, y)
    else:
        print(c.z('[y]NOTE:[c] create operation for cover-units was not succesed:'))
        print(c.z('[y]NOTE:[c]   operation will be generated randomly.'))
    # calc and check
    total = h.do_math(total, operand, number)
    if not check_operation_by_negative_effects(negative_allowed, 'c', total, operands, range_params[0], combs_neg):
        operand, number, total, combs_pos, combs_pos = create_operation_cover(*backup)
    return operand, number, total, combs_pos, combs_neg
def extract_random_y_from_combs(combs, x):
    x_pairs = [(i, y) for i, y in combs if i == x]
    if x_pairs:
        xy_pair = random.choice(list(x_pairs))
        y = xy_pair[1]
        combs.remove(xy_pair)
        return y, combs
    return False, combs

# common sequence/random.cover
def choose_operand(operands):
    operations, weights = zip(*operands.items())
    operand = random.choices(operations, weights=weights, k=1)[0]
    return operand
def create_random_number(range_params, decimal_params):
    range_values = (int(i) for i in range_params)
    # генерировать float или int
    if decimal_params['precision']:
        # с какой вероятностью генерировать float
        if int(decimal_params['probability']) > random.randint(0, 100):
            number = random.uniform(*range_values)
            # до скольки знаков после запятой должен быть float
            return h.dec(format(number, f".{decimal_params['precision']}f"))
        return h.dec(random.randint(*range_values))
    return h.dec(random.randint(*range_values))
def check_operation_by_negative_effects(negative_allowed, kind, total, operands, min_range, combs_neg=False):
    if negative_allowed:
       return True
    if total >= 0 and total < 0:     return False
    if total <  0 and total < total: return False
    if kind == 'r':
        min_possible_value = h.dec(min_range)
    if kind == 'c':
        x = total % 10
        x_pairs = [(i, y) for i, y in combs_neg if i == x]
        if x_pairs:
            min_y = min(x_pairs, key=lambda pair: pair[1])[1]
            min_possible_value = replace_units(h.dec(min_range), min_y)
        else:
            min_possible_value = h.dec(min_range)
    if (len(operands) == 1) and ('-' in operands) and (total - min_possible_value < 0):
        print(c.z('[r]FAIL:[c] The sequence [r]was not created[c] due to conflicting parameters:'))
        print(c.z('[y]FAIL:[c]   - Negative numbers are not allowed.'))
        print(c.z('[y]FAIL:[c]   - Only "-" operands are used.'))
        print(c.z('[y]FAIL:[c]   - The current result minus the minimum possible value is less than zero.'))
        print(c.z('[y]FAIL:[c]   - The limit has been reached.'))
        exit(2)
    return True
def replace_units(number, x):
    if not (1 <= x <= 9):
        raise ValueError("must be 1 <= x <= 9")
    integer_part = int(number // Decimal(1))
    fractional_part = number % Decimal(1)
    new_integer_part = (integer_part // 10) * 10 + x
    return Decimal(new_integer_part) + fractional_part
