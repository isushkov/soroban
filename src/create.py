import random
# src
from src.config import Config
from src.params import parse_params, params2basename
import src.sequence as s
# src/view
from src.view.create import ViewCreate
# src/helpers
from src.helpers.cmd import cmd
import src.helpers.colors as c
import src.helpers.fo as fo

# init
def create(path, params):
    cnf = Config()
    view = ViewCreate(cnf.w)
    view.render_title('[y]CREATING')
    view.status = ''
    prepare_fs()
    params = parse_params(params)
    sequence = create_sequence_start(view, params[0], params[1]) + '\n'
    for i,seq_params in enumerate(params[1:]):
        kind = seq_params['kind']
        view.render_seq_header(i, kind, seq_params)
        is_roundtrip = seq_params['optional']['roundtrip']
        new_sequence = ''
        if kind == 'p':  new_sequence += create_sequence_progression(view, seq_params, s.safe_eval(sequence))
        if kind == 'r':  new_sequence += create_sequence_random(view, seq_params, s.safe_eval(sequence))
        if kind == 'c':  new_sequence += create_sequence_cover(view, seq_params, s.safe_eval(sequence))
        if is_roundtrip: new_sequence += create_sequence_roundtrip(view, new_sequence)
        sequence += new_sequence.strip() + '\n'
    view.disp_status()
    # save
    # TODO: redo safe_eval
    # data = f'{sequence}= {s.safe_eval(sequence)}'
    data = f'{sequence}= {s.safe_eval_2(sequence)}'

    path = path if path else f"./data/{params2basename(params)}.txt"
    save_file(path, data)
    return path

# fs
def prepare_fs():
    cmd('mkdir -p ./data')
def save_file(path, data):
    fo.str2txt(data, path)
    c.p(f'[g]Exercise was created:[c] {path}')

# start/roundtrip
def create_sequence_start(view, start_param, seq_params):
    view.upd_legend('start')
    operands, range_params, length = seq_params['required'].values()
    allow_neg, decimal_params, _ = seq_params['optional'].values()
    operand = choose_operand(operands)
    if start_param == 'r':
        _, number_str = s.split_operation(create_operation_random(view, 0, operand, range_params, decimal_params, allow_neg))
        second = s.tonum(number_str)
    else:
        second = s.tonum(start_param)
    first = s.tonum(second)
    check_neg(s.do_math(first, operand, second), allow_neg)
    view.upd_status('[b]S ')
    return s.tostr(second)
def create_sequence_roundtrip(view, sequence):
    view.upd_legend('roundtrip')
    operations = sequence.split()
    operations.reverse()
    sequence = ' '+' '.join([switch_operand(operation.strip()) for operation in operations])
    view.upd_status('[b]'+('<'*len(operations))+' ')
    return sequence
def switch_operand(operation):
    operand_old = [operand for operand in '+-*/' if operand in operation][0]
    return operation.replace(operand_old, {'+':'-','-':'+','*':'/','/':'*'}[operand_old])

# progression
def create_sequence_progression(view, seq_params, first):
    view.upd_legend('progression')
    new_sequence = ''
    operands, range_params, length = seq_params['required'].values()
    allow_neg, _, _ = seq_params['optional'].values()
    diff = range_params[0]
    first = first
    for _ in range(int(length)):
        operand = choose_operand(operands)
        operation, first = create_operation_progression(first, operand, diff, allow_neg, first)
        view.upd_status('[b]P')
        new_sequence += operation
    view.upd_status(' ')
    return new_sequence
def create_operation_progression(first, operand, diff, allow_neg):
    second = s.do_math(s.tonum(first), operand, s.tonum(diff))
    check_neg(s.do_math(first, operand, second), allow_neg)
    return f' {s.add_sign(second)}', second

# random
def create_sequence_random(view, seq_params, first):
    view.upd_legend('random')
    new_sequence = ''
    operands, range_params, length = seq_params['required'].values()
    allow_neg, decimal_params, _ = seq_params['optional'].values()
    for i in range(int(length)):
        operand = choose_operand(operands)
        new_sequence += create_operation_random(view, first, operand, range_params, decimal_params, allow_neg)
        view.upd_status('[b]R')
    view.upd_status(' ')
    return new_sequence
def create_operation_random(view, first, operand, range_params, decimal_params, allow_neg):
    # is this possible?
    if not check_neg(s.do_math(first, operand, range_params[0]), allow_neg, exit_policy=0):
        operand = '+'
        shift_min, shift_max = -75, +75
        new_min_range,_ = change_range('min', shift_min, range_params)
        _,new_max_range = change_range('max', shift_max, range_params)
        new_range = [new_min_range, new_max_range]
        view.upd_status_random('[r]e', new_range)
        return create_operation_random(view, first, operand, new_range, decimal_params, allow_neg)
    second = s.tonum(generate_random_number(range_params, decimal_params))
    # no luck this time
    if not check_neg(s.do_math(first, operand, second), allow_neg, exit_policy=0):
        side, shift = 'max', -75
        new_range = change_range('max', -75, range_params)
        view.upd_status_random('[y]n', new_range)
        return create_operation_random(view, first, operand, new_range, decimal_params, allow_neg)
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
def create_sequence_cover(view, seq_params, first):
    view.upd_legend('cover')
    operands, range_params, length = seq_params['required'].values()
    allow_neg, decimal_params, _ = seq_params['optional'].values()
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
    while combs['+'] or combs['-']:
        len_seq = len(new_sequence.split())
        if not view.calls_cover_len_less and length and len_seq > int(length):
            view.render_cover_len('less', length, len_seq)
            view.calls_cover_len_less += 1
        # prepare operand
        operand = choose_operand(operands)
        # prepare random_number
        random_operation = create_operation_random(view, first, operand, range_params, decimal_params, allow_neg)
        _, random_number_str = s.split_operation(random_operation)
        random_number = s.tonum(random_number_str)
        # create operation
        operation, first, combs = create_operation_cover(view, first, operand, allow_neg, combs, random_number)
        new_sequence += operation
    # add extra random operations
    len_seq += 1
    while len_seq < int(length):
        if not view.calls_cover_len_more:
            view.upd_legend('random')
            view.render_cover_len('more', length, len_seq)
            view.calls_cover_len_more += 1
        operand = choose_operand(operands)
        new_sequence += create_operation_random(view, first, operand, range_params, decimal_params, allow_neg)
        view.upd_status('[b]R')
        len_seq += 1
    view.upd_status(' ')
    return new_sequence
def create_operation_cover(view, first, operand, allow_neg, combs, random_number):
    y = first % 10
    yx_pairs = list(combs[operand])
    # 1. (y,x) pairs exitst. remove pair, done.
    y_pairs = allow_filter_pairs_by_neg(first, operand, random_number, get_y_pairs(yx_pairs, y), allow_neg)
    if y_pairs:
        view.upd_status('[b]C[x]')
        x = random.choice(y_pairs)[1]
        second = replace_units(random_number, x)
        combs[operand].remove((y,x))
        return f' {operand}{s.del_sign(second)}', s.do_math(first, operand, second), combs
    # 2. (y,_) init new chain
    y_pairs = allow_filter_pairs_by_neg(first, operand, random_number, yx_pairs, allow_neg)
    if y_pairs:
        view.upd_status('[y]C[x]')
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
        if operand == '-' and not allow_neg and newchain_first < 10:
            view.upd_status('[r]C[x]')
            newchain_first += 10
        return f' {operand}{s.del_sign(newchain_number)}', newchain_first, combs
    # 3. (_,_) reduce power neg filters by "adding mass" and try again.
    view.upd_status('[r]R[x]')
    return f' +{random_number}', s.do_math(first, '+', random_number), combs
def get_y_pairs(combs_op, y):
    return [(y_filtered, x) for (y_filtered, x) in combs_op if y == y_filtered]
def allow_filter_pairs_by_neg(first, operand, random_number, pairs, allow_neg):
    positive_pairs = []
    for (y,x) in pairs:
        predicted_number = replace_units(random_number, x)
        if not check_neg(s.do_math(first, operand, predicted_number), allow_neg, exit_policy=0):
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
def check_neg(number, allow_neg, exit_policy=1):
    """exit_policy:
       0 - exit: no
       1 - exit: yes
    """
    if allow_neg:
        # return True
        c.p(f'[y]TODO:[c] allow_neg')
        exit(2)
    if number < 0:
        if exit_policy == 0:
            return False
        raise Exception(c.z(f'[r]ERROR:[c] number < 0 and neg not allowed: {number}'))
    return True
