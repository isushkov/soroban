import random
from src.params import parse_params, params2basename
import src.sequence as s
import src.helpers.colors as c
import src.helpers.fo as fo
from src.helpers.cmd import cmd

# init
def create(arg_path, arg_params):
    prepare_fs()
    print(c.center(c.z(f' [y]CREATING '), 94, '=', 'x'))
    params = parse_params(arg_params)
    sequence = create_sequence_start(params[0], params[1]) + '\n'
    for i,seq_params in enumerate(params[1:]):
        kind = seq_params['kind']
        c.p(f'[g]sequence {i} ({render_kind(kind)}):')
        c.p(f'  [g]required:[c] {seq_params["required"]}')
        c.p(f'  [g]optional:[c] {seq_params["optional"]}')
        is_roundtrip = seq_params['optional']['roundtrip']
        new_sequence = ''
        if kind == 'p':  new_sequence += create_sequence_progression(seq_params, s.safe_eval(sequence))
        if kind == 'r':  new_sequence += create_sequence_random(seq_params, s.safe_eval(sequence))
        if kind == 'c':  new_sequence += create_sequence_cover(seq_params, s.safe_eval(sequence))
        if is_roundtrip: new_sequence += create_sequence_roundtrip(new_sequence)
        sequence += new_sequence.strip() + '\n'
    # save
    data = f'{sequence}= {s.safe_eval(sequence)}'
    path = arg_path if arg_path else f"./data/{params2basename(params)}.txt"
    save_file(path, data)
    return path
# common
def prepare_fs():
    cmd('mkdir -p ./data')
def render_kind(kind):
    return {'p':'progression', 'r':'random', 'c':'covered'}[kind]
def save_file(path, data):
    cmd('mkdir -p ./data')
    fo.str2txt(data, path)
    c.p(f'[g]Exercise was created:[c] {path}')
    print()

# start/roundtrip
def create_sequence_start(start_param, seq_params):
    c.p(f'[g]start with:[c] {start_param}')
    operands, range_params, length = seq_params['required'].values()
    negative_allowed, decimal_params, _ = seq_params['optional'].values()
    operand = choose_operand(operands)
    if start_param == 'r':
        _, number_str = s.split_operation(create_operation_random(operand, range_params, decimal_params, negative_allowed, 0))
        number = s.dec(number_str)
    else:
        number = s.dec(start_param)
    total = s.dec(number)
    if not negative_politic_check(negative_allowed, total, operand, number):
        c.p('[y]NOTE: [r]<start-number>[c] does not satisfy [y]the negative numbers policy[c].')
        c.p('[y]NOTE: [r]changed to "0".')
        number = 0
    return s.num2str(number)
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
    number = s.do_math(s.dec(first), operand, s.dec(diff))
    if not negative_politic_check(negative_allowed, total, operand, number):
        c.p('[r]ERROR: progression-operation[c] does not satisfy [y]the negative numbers policy[c].')
        c.p('[r]ERROR: exit.')
        exit(2)
    return f' {s.add_sign(number)}', number

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
        number = s.dec(generate_random_number(range_params, decimal_params))
        return f' {operand}{s.num2str(number)}'
    # minus
    if not negative_politic_check(negative_allowed, total, operand, range_params[0]):
        side, shift = 'min', -70
        c.p('[y]NOTE: Random-operation[c] has conflicting parameters:')
        c.p('[y]NOTE:[c]   - Negative numbers are not allowed.')
        c.p('[y]NOTE:[c]   - Only "-" operands are used.')
        c.p('[y]NOTE:[c]   - The current result minus the minimum possible value is less than zero.')
        c.p('[y]NOTE:[c]   - The limit has been reached.')
        c.p(f'[y]NOTE:[c]   replacing by number with [r]"+"[c] and changed range [r]{side}:{s.add_sign(shift)}%[c]')
        return create_operation_random('+', change_range(side, shift, range_params), decimal_params, negative_allowed, total)
    number = s.dec(generate_random_number(range_params, decimal_params))
    if not negative_politic_check(negative_allowed, total, operand, number):
        side, shift = 'max', -70
        c.p('[y]NOTE: Random-operation[c] does not satisfy [r]the negative numbers policy:')
        c.p(f'[y]NOTE:[c]   replacing by number with changed range [r]{side}:{s.add_sign(shift)}%[c]')
        return create_operation_random(operand, change_range(side, shift, range_params), decimal_params, negative_allowed, total)
    return f' {operand}{s.del_sign(number)}'
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
            return s.dec(format(number, f".{decimal_params['precision']}f"))
        return s.dec(random.randint(*range_values))
    return s.dec(random.randint(*range_values))
def change_range(shift_type, shift_percent, range_values):
    min_value, max_value = range_values
    shift_value = int((int(max_value) - int(min_value)) * (shift_percent / 100))
    if shift_type == 'min':
        new_min = int(min_value) - shift_value
        return (new_min, max_value)
    if shift_type == 'max':
        new_max = int(max_value) + shift_value
        return (min_value, new_max)

# cover
def create_sequence_cover(seq_params, total):
    new_sequence = ''
    operands, range_params, length = seq_params['required'].values()
    negative_allowed, decimal_params, _ = seq_params['optional'].values()
    # TODO: cover-units decimal
    if decimal_params['precision']: c.todo('cover-units for decimal')
    # TODO: cover-units for "*/"
    if '*' in operands or '/' in operands: c.todo('cover-units for "*/"')
    combs_tmp = {(y,x) for y in range(0, 10) for x in range(1, 10)}
    combs_pos = combs_tmp if '+' in operands else {}
    combs_neg = combs_tmp if '-' in operands else {}
    is_notified = False
    while combs_pos or combs_neg:
        # если был указан length и length меньше чем потребовалось для подбора всех комбинаций
        if length and len(new_sequence.split()) > int(length) and not is_notified:
            c.p(f'[y]NOTE:[c] Not all numbers have been generated yet for possible combinations of units:')
            c.p(f'[y]NOTE:[c]   The specified [y]length in the parameters [y]will be ignored.')
            c.p(f'[y]NOTE:[c]   the specified length in the parameters is {length}.')
            c.p(f'[y]NOTE:[c]   the current length is [y]{len(new_sequence.split())}.')
            is_notified = True
        operand = choose_operand(operands)
        combs = combs_pos if operand == '+' else combs_neg
        operation, combs, total = create_operation_cover(operand, range_params, decimal_params, negative_allowed, total, combs)
        if operand in '+': combs_pos = combs
        if operand in '-': combs_neg = combs
        new_sequence += operation
    # если был указан length, после того как все комбинации подобраны - генерировать числа рандомно.
    is_notified = False
    while len(new_sequence.split()) <= int(length):
        if not is_notified:
            c.p(f'[y]NOTE:[c] All combinations were matched:')
            c.p(f'[y]NOTE:[y]   The rest of the sequence will be generated randomly.')
            c.p(f'[y]NOTE:[c]   the current length is [y]{len(new_sequence.split())}.')
            c.p(f'[y]NOTE:[c]   the specified length in the parameters is [y]{length}.')
            is_notified = True
        operand = choose_operand(operands)
        new_sequence += create_operation_random(operand, range_params, decimal_params, negative_allowed, total)
    return new_sequence
def create_operation_cover(operand, range_params, decimal_params, negative_allowed, total, combs):
    # create random number, get y
    _, number_str = s.split_operation(create_operation_random(operand, range_params, decimal_params, negative_allowed, total))
    number = s.dec(number_str)
    y = total % 10
    # add offset for units
    y_pairs = get_y_pairs(combs, y)
    if not y_pairs:
        # forced - создать операцию и добавить ее к sequence, после чего у total будут y_pairs.
        c.p('[y]NOTE:[c] cover-operation - [y]no combinations left[c] for the chain of operations.')
        c.p('[y]NOTE:[c]   the operation will be forcibly selected to start a new chain.')
        # выбрать рандомную пару из оставшихся, извлечь "y"
        forced_y = random.choice(list(combs))[0]
        # посчитать единицы и заменить их в number
        if operand == '+': forced_x = abs(forced_y - y)
        if operand == '-': forced_x = abs(y - forced_y)
        forced_number = replace_units(number, forced_x)
        # добавляем получившееся значение в sequence
        forced_operation = f' {operand}{s.del_sign(forced_number)}'
        # total = s.do_math(total, operand, number)
        if operand == '+': total += forced_number
        if operand == '-': total -= forced_number
        # create_operation_cover снова для уже подходящего total
        operation, combs, total = create_operation_cover(operand, range_params, decimal_params, negative_allowed, total, combs)
        two_operations = forced_operation + operation
        return two_operations, combs, total
    # второе число получено
    x = random.choice(y_pairs)[1]
    number = replace_units(number, x)
    # check negative politic
    if not negative_politic_check(negative_allowed, total, operand, number):
        side, shift = 'max', -70
        c.p('[y]NOTE: Cover-operation[c] does not satisfy [r]the negative numbers policy.')
        c.p(f'[y]NOTE:[c]   replacing by number with changed range [r]{side}:{s.add_sign(shift)}%[c]')
        return create_operation_cover(operand, change_range(side, shift, range_params), decimal_params, negative_allowed, total, combs)
    # done. remove pair, go next
    combs.remove((y,x))
    total = s.do_math(total, operand, number)
    return f' {operand}{s.del_sign(number)}', combs, total
def get_y_pairs(combs, y):
    y_pairs = [(y_filtered, x) for (y_filtered, x) in combs if y == y_filtered]
    return y_pairs if y_pairs else False
def replace_units(number, x):
    if not (1 <= x <= 9):
        raise ValueError("must be 1 <= x <= 9")
    integer_part = int(number // s.dec(1))
    fractional_part = number % s.dec(1)
    new_integer_part = (integer_part // 10) * 10 + x
    return s.dec(new_integer_part) + s.dec(fractional_part)
# negative politic
def negative_politic_check(negative_allowed, total, operand, number):
    if negative_allowed: return True
    if operand != '-':   return True
    if s.dec(total) - s.dec(number) < 0:
        return False
    return True
