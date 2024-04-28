import random
from src.params import parse_params, params2basename
import src.sequence as s
import src.helpers.colors as c
import src.helpers.fo as fo
from src.helpers.cmd import cmd

# init
def create(path, params):
    print(c.ljust(c.z(f'[x]========= [y]CREATING '), 94, '=', 'x'))
    prepare_fs()
    params = parse_params(params)
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
    path = path if path else f"./data/{params2basename(params)}.txt"
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

# start/roundtrip
def create_sequence_start(start_param, seq_params):
    operands, range_params, length = seq_params['required'].values()
    negative_allowed, decimal_params, _ = seq_params['optional'].values()
    operand = choose_operand(operands)
    if start_param == 'r':
        _, number_str = s.split_operation(create_operation_random(0, operand, range_params, decimal_params, negative_allowed))
        second = s.tonum(number_str)
    else:
        second = s.tonum(start_param)
    first = s.tonum(second)
    check_negative(s.do_math(first, operand, second), negative_allowed)
    return s.tostr(second)
def create_sequence_roundtrip(sequence):
    operations = sequence.split()
    operations.reverse()
    sequence = ' '+' '.join([switch_operand(operation.strip()) for operation in operations])
    return sequence
def switch_operand(operation):
    operand_old = [operand for operand in '+-*/' if operand in operation][0]
    return operation.replace(operand_old, {'+':'-','-':'+','*':'/','/':'*'}[operand_old])

# progression
def create_sequence_progression(seq_params, first):
    new_sequence = ''
    operands, range_params, length = seq_params['required'].values()
    negative_allowed, _, _ = seq_params['optional'].values()
    diff = range_params[0]
    first = first
    for _ in range(int(length)):
        operand = choose_operand(operands)
        operation, first = create_operation_progression(first, operand, diff,
                                    negative_allowed, first)
        new_sequence += operation
    return new_sequence
def create_operation_progression(first, operand, diff, negative_allowed):
    second = s.do_math(s.tonum(first), operand, s.tonum(diff))
    check_negative(s.do_math(first, operand, second), negative_allowed)
    return f' {s.add_sign(second)}', second

# random
def create_sequence_random(seq_params, first):
    new_sequence = ''
    operands, range_params, length = seq_params['required'].values()
    negative_allowed, decimal_params, _ = seq_params['optional'].values()
    for _ in range(int(length)):
        operand = choose_operand(operands)
        new_sequence += create_operation_random(first, operand, range_params, decimal_params, negative_allowed)
    return new_sequence
def create_operation_random(first, operand, range_params, decimal_params, negative_allowed):
    # is this possible?
    if not check_negative(s.do_math(first, operand, range_params[0]), negative_allowed, exit_policy=0):
        operand = '+'
        shift_min, shift_max = -75, +75
        new_min_range,_ = change_range('min', shift_min, range_params)
        _,new_max_range = change_range('max', shift_max, range_params)
        new_range = [new_min_range, new_max_range]
        note_negative_not_posible('random')
        note_change_operand('random', operand)
        note_change_range('random', 'min', shift_min, range_params, new_range)
        note_change_range('random', 'max', shift_max, range_params, new_range)
        return create_operation_random(first, operand, new_range, decimal_params, negative_allowed)
    second = s.tonum(generate_random_number(range_params, decimal_params))
    # no luck this time
    if not check_negative(s.do_math(first, operand, second), negative_allowed, exit_policy=0):
        side, shift = 'max', -75
        new_range = change_range('max', -75, range_params)
        note_negative_not_satisfy('random')
        note_change_range('random', side, shift, range_params, new_range)
        return create_operation_random(first, operand, new_range, decimal_params, negative_allowed)
    check_negative(s.do_math(first, operand, second), negative_allowed, exit_policy=1)
    c.p(f'[x]>>>>: random-operation: done:[c] operation: {operand}{s.del_sign(second)}')
    c.p(f'[x]>>>>: random-operation:      [c] first,range_params:{(first, range_params)}')
    return f' {operand}{s.del_sign(second)}'
def choose_operand(operands):
    if len(operands) == 1:
        return next(iter(operands))
    operations, weights = zip(*operands.items())
    operand = random.choices(operations, weights=weights, k=1)[0]
    return operand
def generate_random_number(range_params, decimal_params):
    range_values = tuple(int(i) for i in range_params)
    # генерировать float или int
    if decimal_params['precision']:
        # с какой вероятностью генерировать float
        if int(decimal_params['probability']) > random.randint(0, 100):
            second = random.uniform(*range_values)
            # до скольки знаков после запятой должен быть float
            return s.tonum(format(second, f".{decimal_params['precision']}f"))
        return s.tonum(random.randint(*range_values))
    return s.tonum(random.randint(*range_values))

# cover
def create_sequence_cover(seq_params, first):
    operands, range_params, length = seq_params['required'].values()
    negative_allowed, decimal_params, _ = seq_params['optional'].values()
    # TODO: cover-units decimal
    if decimal_params['precision']: c.todo('cover-units for decimal')
    # TODO: cover-units for "*/"
    if '*' in operands or '/' in operands: c.todo('cover-units for "*/"')
    # create cover sequence
    new_sequence = ''
    combs_origin = {(y,x) for y in range(0, 10) for x in range(1, 10)}
    combs = {
        '+': combs_origin.copy() if '+' in operands else set(),
        '-': combs_origin.copy() if '-' in operands else set()
    }
    is_notified = False
    while combs['+'] or combs['-']:
        if length and len(new_sequence.split()) > int(length) and not is_notified:
            is_notified = note_length_less_than_req('cover', length, new_sequence)
        operand = choose_operand(operands)
        if not combs[operand]:
            continue
        operation, first, combs = create_operation_cover(first, operand, range_params, decimal_params, negative_allowed, combs)
        new_sequence += operation
    # add extra random operations
    is_notified = False
    while len(new_sequence.split()) < int(length):
        if not is_notified:
            is_notified = note_length_more_than_req('cover', length, new_sequence)
        operand = choose_operand(operands)
        new_sequence += create_operation_random(first, operand, range_params, decimal_params, negative_allowed)
    return new_sequence
def create_operation_cover(first, operand, range_params, decimal_params, negative_allowed, combs):
    # c.p(f'[b]>>>>: cover-operation:  start. first:{first}, operand:{operand}, range_params:{range_params}')
    # prepare random_number
    random_operation = create_operation_random(first, operand, range_params, decimal_params, negative_allowed)
    _, random_number_str = s.split_operation(random_operation)
    random_number = s.tonum(random_number_str)
    # looking y_pairs
    y = int(first % 10)
    y_pairs = get_y_pairs(combs[operand], y)
    # если пар нет
    if not y_pairs:
        note_pairs_not_exist('cover')
        # add forced_operation
        forced_operation, forced_first = create_operation_forced(first, operand, random_number, negative_allowed, combs)
        return forced_operation, forced_first, combs
    # если пары есть, но они все не удовлетворяют negative_politic
    y_pairs = filter_pairs_by_negative_allowed(first, operand, random_number, y_pairs, negative_allowed)
    if not y_pairs:
        note_pairs_not_satisfy('cover')
        operand = '+'
        note_change_operand('cover', operand)
        # если пар нет (+)
        y_pairs = get_y_pairs(combs[operand], y)
        if not y_pairs:
            # add random_operation
            note_pairs_not_exist('cover')
            return f' {operand}{s.del_sign(random_number)}', s.do_math(first, operand, random_number), combs
        # add forced_operation (+)
        forced_operation, forced_first = create_operation_forced(first, operand, random_number, negative_allowed, combs)
        return forced_operation, forced_first, combs
    # get second
    x = random.choice(y_pairs)[1]
    second = replace_units(random_number, x)
    # done. remove pair, go next
    combs[operand].remove((y,x))
    check_negative(s.do_math(first, operand, second), negative_allowed) # TODO: tmp
    # c.p(f'[g]>>>>: cover-operation:  done. first:{first}, operand:{operand}, second:{second}')
    return f' {operand}{s.del_sign(second)}', s.do_math(first, operand, second), combs
def get_y_pairs(combs_op, y):
    return [(y_filtered, x) for (y_filtered, x) in combs_op if y == y_filtered]
def filter_pairs_by_negative_allowed(first, operand, random_number, y_pairs, negative_allowed):
    positive_pairs = []
    for (y,x) in y_pairs:
        predicted_number = replace_units(random_number, x)
        if not check_negative(s.do_math(first, operand, predicted_number), negative_allowed, exit_policy=0):
            continue
        positive_pairs.append((y,x))
    return positive_pairs
# add random number with "x" from combs
def create_operation_forced(first, operand, random_number, negative_allowed, combs):
    # c.p(f'[r]>>>>: forced-operation:[c] start. first:{first}, operand:{operand}')
    y = int(first % 10)
    pairs = list(combs[operand])
    # если combs пустой
    if not pairs:
        # add random_operation
        note_pairs_not_exist('forced')
        second = replace_units(random_number, random.randint(1, 9))
        return f' {operand}{s.del_sign(second)}', s.do_math(first, operand, second)
    # выбрать пару которая не делают forced_first отрицательным
    if not negative_allowed and operand == '-':
        pairs = []
        for (y,x) in pairs:
            if first - replace_units(random_number, x) < 0:
                continue
            pairs.append((y,x))
        # если таких пар нет
        if not pairs:
            # add random_operation
            operand = '+'
            note_pairs_not_exist('forced')
            note_change_operand('forced', operand)
            second = replace_units(random_number, random.randint(1, 9))
            return f' {operand}{s.del_sign(second)}', s.do_math(first, operand, second)
    # берем пару
    forced_pair = random.choice(pairs)
    forced_y = forced_pair[0]
    if operand == '+': x = (10+forced_y - y) % 10
    if operand == '-': x = (10+y - forced_y) % 10
    # get new operation with new first
    second = replace_units(random_number, x)
    operation = f' {operand}{s.del_sign(second)}'
    forced_first = s.do_math(first, operand, second)
    check_negative(forced_first, negative_allowed) # TODO: tmp
    # c.p(f'[r]>>>>: forced-operation:[c] done. forced_first:{forced_first}, operation:{operation}')
    return operation, forced_first
def replace_units(second, x):
    integer_part = int(second // s.tonum(1))
    fractional_part = second % s.tonum(1)
    new_integer_part = (integer_part // 10) * 10 + x
    return s.tonum(new_integer_part) + s.tonum(fractional_part)

# random/cover:common
def change_range(shift_type, shift_percent, old_range):
    old_range = list(map(int, old_range))
    min_value, max_value = old_range
    shift_value = int((max_value - min_value) * (shift_percent / 100))
    if shift_value == 0: shift_value = 1 if shift_percent != 0 else 0
    if shift_type == 'min':
        min_value -= shift_value
        if min_value < 1:
            min_value = 1
    if shift_type == 'max':
        max_value += shift_value
        if max_value < 1:
            max_value = 1
    if max_value < min_value:
        max_value = min_value
    new_range = [min_value, max_value]
    # ok
    if new_range == old_range:
        raise Exception(c.z(f'[r]ERROR:[c] range the same: {old_range} -> {new_range}'))
    return new_range
def check_negative(number, negative_allowed, exit_policy=1):
    """exit_policy:
       0 - exit: no
       1 - exit: yes
    """
    if negative_allowed:
        # return True
        c.p(f'[y]TODO:[c] negative allowed')
        exit(2)
    if number < 0:
        if exit_policy == 0:
            return False
        raise Exception(c.z(f'[r]ERROR:[c] number < 0 and negative not allowed: {number}'))
    return True

# note.negative
def note_negative_not_posible(kind):
    c.p(f'[y]NOTE: {kind}-operation:[c] has conflicting parameters:')
    c.p('[y]NOTE:[c]   - Negative numbers are not allowed.')
    c.p('[y]NOTE:[c]   - Only "-" operands are used.')
    c.p('[y]NOTE:[c]   - The current result minus the minimum possible value is less than zero.')
    c.p('[y]NOTE:[c]   - The limit has been reached.')
def note_negative_not_satisfy(kind):
    c.p(f'[y]NOTE: {kind}-operation:[c] does not satisfy [r]the negative numbers policy.[x] Trying again..')
# note.change
def note_change_operand(kind, new_operand):
    c.p(f'[y]NOTE: {kind}-operation:[c] changing [r]operand by "{new_operand}".')
def note_change_range(kind, side, shift, old_range, new_range):
    old_range, new_range = map(str, old_range), map(str, new_range)
    c.p(f'[y]NOTE: {kind}-operation:[c] changing [r]range {side}:{s.add_sign(shift)}%[c] [x]([c]{"-".join(old_range)} [x]->[c] {"-".join(new_range)}[x])')
# note.pairs
def note_pairs_not_exist(kind):
    c.p(f'[y]NOTE: {kind}-operation: [r]no y-pairs left[c] for the chain of operations.')
def note_pairs_not_satisfy(kind):
    c.p(f'[y]NOTE: {kind}-operation: [r]all y-pairs for does not satisfy[c] the negative numbers policy.')
# note.extra
def note_length_less_than_req(kind, length, new_sequence):
    c.p(f'[y]NOTE: {kind}-operation:[c] Not all numbers have been generated yet for possible combinations of units:')
    c.p(f'[y]NOTE:[c]   The specified [y]length in the parameters [y]will be ignored.')
    c.p(f'[y]NOTE:[c]   the specified length in the parameters is {length}.')
    c.p(f'[y]NOTE:[c]   the current length is [y]{len(new_sequence.split())}.')
    return True
def note_length_more_than_req(kind, length, new_sequence):
    c.p(f'[y]NOTE: {kind}-operation:[c] All combinations were matched:')
    c.p(f'[y]NOTE:[y]   The rest of the sequence will be generated randomly.')
    c.p(f'[y]NOTE:[c]   the current length is [y]{len(new_sequence.split())}.')
    c.p(f'[y]NOTE:[c]   the specified length in the parameters is [y]{length}.')
    return True
