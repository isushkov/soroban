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
    start_param = params.pop(0)
    sequence = create_sequence_start(start_param, params[0]) + '\n'
    names = []
    for i,seq_params in enumerate(params):
        kind = seq_params['kind']
        print(c.z(f'[g]sequence {i} ({render_kind(kind)}):'))
        print(c.z(f'  [g]required:[c] {seq_params["required"]}'))
        print(c.z(f'  [g]optional:[c] {seq_params["optional"]}'))
        is_roundtrip = seq_params['optional']['roundtrip']
        new_sequence = ''
        if kind == 'p':  new_sequence += create_sequence_progression(seq_params, h.safe_eval(sequence))
        if kind == 'r':  new_sequence += create_sequence_random(seq_params, h.safe_eval(sequence))
        if kind == 'c':  new_sequence += create_sequence_cover(seq_params, h.safe_eval(sequence))
        if is_roundtrip: new_sequence += create_sequence_roundtrip(new_sequence)
        sequence += new_sequence.strip() + '\n'
        names.append(seq_params2part_name(kind, seq_params))
    # save
    data = f'{sequence}= {h.safe_eval(sequence)}'
    path = args.path if args.path else f"./data/x{start_param}_{'_'.join(names)}.txt"
    save_file(path, data)
    return path
# common
def render_kind(kind):
    return {'p':'progression', 'r':'random', 'c':'covered'}[kind]
def seq_params2part_name(kind, seq_params):
    m = {'+':'p', '-':'m', '*':'M', '/':'D'}
    k = {'p':'prog', 'r':'rand', 'c':'covr'}[kind]
    operands = ''.join([f'{m[k]}{v}' for k,v in seq_params['required']['operands'].items()])
    range_params = 'x'.join(str(i) for i in seq_params['required']['range'])
    length = int(seq_params['required']['length'])
    decimal_params = seq_params['optional']['decimal']
    precision = 1 if decimal_params['precision'] else 0
    probability = 1 if decimal_params['probability'] else 0
    negative = f"{1 if seq_params['optional']['negative_allowed'] else 0}"
    decimal = f'{precision}x{probability}'
    roundtrip = f"{1 if seq_params['optional']['roundtrip'] else 0}"
    return f'{k}-{operands}-{range_params}-{length}-n{negative}-d{decimal}-r{roundtrip}'
def save_file(path, data):
    cmd.run('mkdir -p ./data')
    fo.str2txt(data, path)
    print(c.z(f'[g]Exercise was created:[c] {path}'))
    print()

# start/roundtrip
def create_sequence_start(start_param, seq_params):
    print(c.z(f'[g]start with:[c] {start_param}'))
    operands, range_params, length = seq_params['required'].values()
    negative_allowed, decimal_params, _ = seq_params['optional'].values()
    operand = choose_operand(operands)
    if start_param == 'r':
        number = h.dec(create_operation_random(operand, range_params, decimal_params, negative_allowed, 0))
    else:
        number = h.dec(start_param)
    total = h.dec(number)
    if not negative_politic_check(negative_allowed, total, operand, number):
        print(c.z('[y]NOTE: [r]<start-number>[c] does not satisfy [y]the negative numbers policy[c].'))
        print(c.z('[y]NOTE: [r]changed to "0".'))
        number = 0
    return h.num2str(number)
def create_sequence_roundtrip(sequence):
    operations = sequence.split()
    operations.reverse()
    sequence = ' '+' '.join([switch_operand(operation.strip()) for operation in operations])
    return sequence
def switch_operand(operation):
    operand_old = [operand for operand in '+-*/' if operand in operation][0]
    return operation.replace(operand_old, {'+':'-','-':'+','*':'/','/':'*'}[operand_old])

# progression
def create_sequence_progression(seq_params, total):
    new_sequence = ''
    operands, range_params, length = seq_params['required'].values()
    negative_allowed, _, _ = seq_params['optional'].values()
    diff = range_params[0]
    first = total
    for _ in range(int(length)):
        operand = choose_operand(operands)
        operation, first = create_operation_progression(first, operand, diff,
                                    negative_allowed, total)
        new_sequence += operation
    return new_sequence
def create_operation_progression(first, operand, diff, negative_allowed, total):
    number = h.do_math(h.dec(first), operand, h.dec(diff))
    if not negative_politic_check(negative_allowed, total, operand, number):
        print(c.z('[r]ERROR: progression-operation[c] does not satisfy [y]the negative numbers policy[c].'))
        print(c.z('[r]ERROR: exit.'))
        exit(2)
    return f' {h.add_sign(number)}', number

# random
def create_sequence_random(seq_params, total):
    new_sequence = ''
    operands, range_params, length = seq_params['required'].values()
    negative_allowed, decimal_params, _ = seq_params['optional'].values()
    for _ in range(int(length)):
        operand = choose_operand(operands)
        new_sequence += create_operation_random(operand, range_params, decimal_params, negative_allowed, total)
    return new_sequence
def create_operation_random(operand, range_params, decimal_params, negative_allowed, total):
    if operand in '+*/':
        number = h.dec(generate_random_number(range_params, decimal_params))
        return f' {operand}{h.num2str(number)}'
    # minus
    if not negative_politic_check(negative_allowed, total, operand, range_params[0]):
        print(c.z('[r]ERROR:[c] Negative politic. Conflicting parameters:'))
        print(c.z('[r]ERROR:[c]   - Negative numbers are not allowed.'))
        print(c.z('[r]ERROR:[c]   - Only "-" operands are used.'))
        print(c.z('[r]ERROR:[c]   - The current result minus the minimum possible value is less than zero.'))
        print(c.z('[r]ERROR:[c]   - The limit has been reached.'))
        print(c.z('[r]ERROR: Operand will be replaced by "+".'))
        return create_operation_random('+', range_params, decimal_params, negative_allowed, total)
    number = h.dec(generate_random_number(range_params, decimal_params))
    if not negative_politic_check(negative_allowed, total, operand, number):
        print(c.z('[y]NOTE:[c] [r]random-operation[c] does not satisfy [y]the negative numbers policy.'))
        print(c.z('[y]NOTE:[c] trying again..'))
        return create_operation_random(operand, range_params, decimal_params, negative_allowed, total)
    return f' {operand}{h.del_sign(number)}'
def choose_operand(operands):
    operations, weights = zip(*operands.items())
    operand = random.choices(operations, weights=weights, k=1)[0]
    return operand
def generate_random_number(range_params, decimal_params):
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

# cover
def create_sequence_cover(seq_params, total):
    new_sequence = ''
    operands, range_params, length = seq_params['required'].values()
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
    combs_tmp = {(y,x) for y in range(0, 10) for x in range(1, 10)}
    combs_pos = combs_tmp if '+' in operands else {}
    combs_neg = combs_tmp if '-' in operands else {}
    is_notified = False
    while combs_pos or combs_neg:
        operand = choose_operand(operands)
        combs = combs_pos if operand == '+' else combs_neg
        operation, combs, total = create_operation_cover(operand, range_params, decimal_params, negative_allowed, total, combs)
        if operand in '+': combs_pos = combs
        if operand in '-': combs_neg = combs
        new_sequence += operation
        # если был указан length и length меньше чем потребовалось для подбора всех комбинаций
        if length and len(new_sequence.split()) >= int(length) and not is_notified:
            print(c.z(f'[y]NOTE:[c] Not all numbers have been generated yet for possible combinations of units.'))
            print(c.z(f'[y]NOTE:[c] The specified [y]length in the parameters [y]will be ignored:'))
            print(c.z(f'[y]NOTE:[c]   the specified length in the parameters is {length}.'))
            print(c.z(f'[y]NOTE:[c]   the current length is [y]{len(new_sequence.split())}.'))
            print(new_sequence)
            is_notified = True
    # если был указан length, после того как все комбинации подобраны - генерировать числа рандомно.
    is_notified = False
    while len(new_sequence.split()) <= int(length):
        if not is_notified:
            print(c.z(f'[y]NOTE:[c] All combinations were matched:'))
            print(c.z(f'[y]NOTE:[y] The rest of the sequence will be generated randomly:'))
            print(c.z(f'[y]NOTE:[c]   the current length is [y]{len(new_sequence.split())}.'))
            print(c.z(f'[y]NOTE:[c]   the specified length in the parameters is [y]{length}.'))
            is_notified = True
        operand = choose_operand(operands)
        new_sequence += create_operation_random(operand, range_params, decimal_params, negative_allowed, total)
    return new_sequence
def create_operation_cover(operand, range_params, decimal_params, negative_allowed, total, combs):
    # create random number
    number = h.dec(create_operation_random(operand, range_params, decimal_params, negative_allowed, total))
    # add offset for units
    y = total % 10
    x = extract_random_x_from_combs(combs, y)
    is_pair_exist = True
    if not x:
        is_pair_exist = False
        print(c.z('[y]NOTE:[c] cover-operation was not created: [y]new combinations not found[c]. operation will be generated randomly..'))
        x = random.randint(1, 9)
    number = replace_units(number, x)
    # check negative politic
    if not negative_politic_check(negative_allowed, total, operand, number):
        print(c.z('[y]NOTE:[c] [r]cover-operation[c] does not satisfy [y]the negative numbers policy.'))
        print(c.z('[y]NOTE:[c] trying again..'))
        return create_operation_cover(operand, range_params, decimal_params, negative_allowed, total, combs)
    # done. remove pair
    if is_pair_exist:
        combs.remove((y,x))
    total = h.do_math(total, operand, number)
    return f' {operand}{h.del_sign(number)}', combs, total
def extract_random_x_from_combs(combs, y):
    y_pairs = [(y_filtered, x) for (y_filtered, x) in combs if y == y_filtered]
    if not y_pairs:
        return False
    choice = random.choice(y_pairs)[1]
    return choice
def replace_units(number, x):
    if not (1 <= x <= 9):
        raise ValueError("must be 1 <= x <= 9")
    integer_part = int(number // h.dec(1))
    fractional_part = number % h.dec(1)
    new_integer_part = (integer_part // 10) * 10 + x
    return h.dec(new_integer_part) + h.dec(fractional_part)

# negative politic
def negative_politic_check(negative_allowed, total, operand, number):
    if negative_allowed: return True
    if operand != '-':   return True
    if h.dec(total) - h.dec(number) < 0:
        print('>>>>')
        print('total:', h.dec(total))
        print('number:', h.dec(number))
        return False
    return True
