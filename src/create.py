import random
# src
from src.params import parse_params, params2basename
import src.sequence as s
# src/view
from src.view.create import ViewCreate
# src/helpers
from src.helpers.cmd import cmd
import src.helpers.colors as c
import src.helpers.fo as fo

view = ViewCreate()

# init
def create(path, params):
    view.render_title('[y]CREATING')
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
    view.display_status()
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
    for i in range(int(length)):
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
        view.upd_status_random('[r]e', new_range)
        return create_operation_random(first, operand, new_range, decimal_params, negative_allowed)
    second = s.tonum(generate_random_number(range_params, decimal_params))
    # no luck this time
    if not check_negative(s.do_math(first, operand, second), negative_allowed, exit_policy=0):
        side, shift = 'max', -75
        new_range = change_range('max', -75, range_params)
        view.upd_status_random('[y]n', new_range)
        return create_operation_random(first, operand, new_range, decimal_params, negative_allowed)
    return f' {operand}{s.del_sign(second)}'
def choose_operand(operands):
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
            is_notified = view.render_note_cover_len('less', length, len(new_sequence.split()))
        # prepare operand
        operand = choose_operand(operands)
        # prepare random_number
        random_operation = create_operation_random(first, operand, range_params, decimal_params, negative_allowed)
        _, random_number_str = s.split_operation(random_operation)
        random_number = s.tonum(random_number_str)
        # create operation
        operation, first, combs = create_operation_cover(first, operand, negative_allowed, combs, random_number)
        new_sequence += operation
    # add extra random operations
    is_notified = False
    while len(new_sequence.split()) < int(length):
        if not is_notified:
            is_notified = view.render_note_cover_len('more', length, len(new_sequence.split()))
        operand = choose_operand(operands)
        new_sequence += create_operation_random(first, operand, range_params, decimal_params, negative_allowed)
    return new_sequence
def create_operation_cover(first, operand, negative_allowed, combs, random_number):
    y = first % 10
    yx_pairs = list(combs[operand])
    # 1. (y,x) pairs exitst. remove pair, done.
    y_pairs = filter_pairs_by_negative_allowed(first, operand, random_number, get_y_pairs(yx_pairs, y), negative_allowed)
    if y_pairs:
        view.upd_status('[b]D[x]')
        x = random.choice(y_pairs)[1]
        second = replace_units(random_number, x)
        combs[operand].remove((y,x))
        return f' {operand}{s.del_sign(second)}', s.do_math(first, operand, second), combs
    # 2. (y,_) init new chain
    y_pairs = filter_pairs_by_negative_allowed(first, operand, random_number, yx_pairs, negative_allowed)
    if y_pairs:
        view.upd_status('[y]N[x]')
        newchain_y = random.choice(y_pairs)[0]
        # получение разряда единиц. +10 гарантирует положительный результат
        if operand == '+': x = (10+newchain_y - y) % 10
        if operand == '-': x = (10+y - newchain_y) % 10
        newchain_number = replace_units(random_number, x)
        newchain_first = s.do_math(first, operand, newchain_number)
        # бесконечный цикл когда "-" единственный операнд. нехватает "массы". ex:
        #   first, random_number:  7, 3
        #   yx_pairs: [(2, 6)]
        #   newchain_pair: (2, 6)
        #     7(7) - 5(3->5) = 2(2)
        if operand == '-' and not negative_allowed and newchain_first < 10:
            view.upd_status('[r]N[x]')
            newchain_first += 10
        return f' {operand}{s.del_sign(newchain_number)}', newchain_first, combs
    # 3. (_,_) reduce power negative filters by "adding mass" and try again.
    view.upd_status('[r]R[x]')
    return f' +{random_number}', s.do_math(first, '+', random_number), combs
def get_y_pairs(combs_op, y):
    return [(y_filtered, x) for (y_filtered, x) in combs_op if y == y_filtered]
def filter_pairs_by_negative_allowed(first, operand, random_number, pairs, negative_allowed):
    positive_pairs = []
    for (y,x) in pairs:
        predicted_number = replace_units(random_number, x)
        if not check_negative(s.do_math(first, operand, predicted_number), negative_allowed, exit_policy=0):
            continue
        positive_pairs.append((y,x))
    return positive_pairs
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
