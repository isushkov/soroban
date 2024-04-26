import random
from src.params import parse_params, params2basename
import src.sequence as s
import src.helpers.colors as c
import src.helpers.fo as fo
from src.helpers.cmd import cmd

# init
def create(path, params):
    prepare_fs()
    print(c.center(c.z(f' [y]CREATING '), 94, '=', 'x'))
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
    print()

# start/roundtrip
def create_sequence_start(start_param, seq_params):
    c.p(f'[g]start with:[c] {start_param}')
    operands, range_params, length = seq_params['required'].values()
    negative_allowed, decimal_params, _ = seq_params['optional'].values()
    operand = choose_operand(operands)
    if start_param == 'r':
        _, number_str = s.split_operation(create_operation_random(operand, range_params, decimal_params, negative_allowed, 0, range_params))
        number = s.dec(number_str)
    else:
        number = s.dec(start_param)
    total = s.dec(number)
    if not negative_politic_check(total, operand, number, negative_allowed):
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
    if not negative_politic_check(total, operand, number, negative_allowed):
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
    # is this possible?
    if not negative_politic_check(total, operand, range_params[0], negative_allowed):
        shift_min, shift_max = -200, +200
        new_min_range,_ = change_range('min', shift_min, range_params)
        _,new_max_range = change_range('max', shift_max, range_params)
        new_range = [new_min_range, new_max_range]
        # note_negative_not_posible('r')
        # note_change_operand('+')
        # note_change_range('min', shift_min, range_params, new_range)
        # note_change_range('max', shift_max, range_params, new_range)
        return create_operation_random('+', new_range, decimal_params, negative_allowed, total)
    number = s.dec(generate_random_number(range_params, decimal_params))
    # no luck this time
    if not negative_politic_check(total, operand, number, negative_allowed):
        side, shift = 'max', -75
        new_range = change_range('max', -75, range_params)
        # note_negative_not_satisfy('r')
        # note_change_range(side, shift, range_params, new_range)
        return create_operation_random(operand, new_range, decimal_params, negative_allowed, total)
    # c.p('[x]>>>>: random-operation: done..')
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

# cover
def create_sequence_cover(seq_params, total):
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
        '+': combs_origin.copy() if '+' in operands else {},
        '-': combs_origin.copy() if '-' in operands else {}
    }
    is_notified = False
    while combs['+'] or combs['-']:
        if length and len(new_sequence.split()) > int(length) and not is_notified:
            is_notified = note_length_less_than_req(length, new_sequence)
        operand = choose_operand(operands)
        if not combs[operand]:
            continue
        operation, total, combs = create_operation_cover(operand, range_params, decimal_params, negative_allowed, total, combs)
        new_sequence += operation
    # add extra random operations
    is_notified = False
    while len(new_sequence.split()) <= int(length):
        if not is_notified:
            is_notified = note_length_more_than_req(length, new_sequence)
        operand = choose_operand(operands)
        new_sequence += create_operation_random(operand, range_params, decimal_params, negative_allowed, total)
    return new_sequence
def create_operation_cover(operand, range_params, decimal_params, negative_allowed, total, combs):
    # c.p('[b]>>>>: cover-operation: start..')
    if total < 0:
        c.todo(f'negative. total: {total}')
    # prepare random_number
    random_operation = create_operation_random(operand, range_params, decimal_params, negative_allowed, total)
    _, random_number_str = s.split_operation(random_operation)
    random_number = s.dec(random_number_str)
    # looking y_pairs
    y = int(total % 10)
    y_pairs = get_y_pairs(combs[operand], y)
    # если пар нет
    if not y_pairs:
        # note_cover_no_pairs()
        # add forced_operation
        forced_operation, forced_total = create_operation_forced(operand, range_params, decimal_params, negative_allowed, total, combs, random_number)
        return forced_operation, forced_total, combs
    # если пары есть, но они все не удовлетворяют negative_politic
    y_pairs = filter_pairs_by_negative_politic(total, operand, random_number, negative_allowed, y_pairs)
    if not y_pairs:
        # note_negative_not_satisfy('c')
        operand = '+'
        # note_change_operand(operand)
        # если для '+' пар нет
        y_pairs = get_y_pairs(combs[operand], y)
        if not y_pairs:
            # note_cover_no_pairs()
            # add random_operation
            return f' {operand}{s.del_sign(random_number)}', s.do_math(total, operand, random_number), combs
        # add forced_operation
        forced_operation, forced_total = create_operation_forced(operand, range_params, decimal_params, negative_allowed, total, combs, random_number)
        return forced_operation, forced_total, combs
    # get second number
    x = random.choice(y_pairs)[1]
    number = replace_units(random_number, x)
    # done. remove pair, go next
    combs[operand].remove((y,x))
    # c.p('[g]>>>>: cover-operation: done..')
    return f' {operand}{s.del_sign(number)}', s.do_math(total, operand, number), combs
def get_y_pairs(combs_op, y):
    return [(y_filtered, x) for (y_filtered, x) in combs_op if y == y_filtered]
def filter_pairs_by_negative_politic(total, operand, random_number, negative_allowed, y_pairs):
    positive_y_pairs = []
    for (y, x) in y_pairs:
        predicted_number = replace_units(random_number, x)
        if not negative_politic_check(total, operand, predicted_number, negative_allowed):
            continue
        positive_y_pairs.append((y,x))
    return positive_y_pairs
def create_operation_forced(operand, range_params, decimal_params, negative_allowed, total, combs, random_number):
    # c.p(f'[y]NOTE:[c] Cover-operation - [r]Adding forced-operation..')
    y = int(total % 10)
    forced_pair = random.choice(list(combs[operand]))
    forced_y = forced_pair[0]
    if operand == '+': forced_x = (10+forced_y - y) % 10
    if operand == '-': forced_x = (10+y - forced_y) % 10
    # get new operation with new total
    forced_number = replace_units(random_number, forced_x)
    forced_operation = f' {operand}{s.del_sign(forced_number)}'
    forced_total = s.do_math(total, operand, forced_number)
    # print('operand:         ', operand)
    # print('combs[operand]:  ', combs[operand])
    # print('forced_pair:     ', forced_pair)
    # print('total, y:        ', total, y)
    # print('forced_x:        ', forced_x)
    # print('forced_y:        ', forced_y)
    # print('forced_total:    ', forced_total)
    # print('forced_operation:', forced_operation)
    return forced_operation, forced_total
def replace_units(number, x):
    integer_part = int(number // s.dec(1))
    fractional_part = number % s.dec(1)
    new_integer_part = (integer_part // 10) * 10 + x
    return s.dec(new_integer_part) + s.dec(fractional_part)
# negative politic
def negative_politic_check(total, operand, number, negative_allowed):
    if operand != '-':
        return True
    # TODO пока не важно можно или нельзя. отрицательные числа не работают в любом случае
    # if negative_allowed:
    #    return True
    if s.do_math(total, operand, s.dec(s.del_sign(number))) < 0:
        return False
    return True
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
    if new_range == old_range:
        raise Exception(c.z(f'[r]ERROR:[c] range the same: {old_range} -> {new_range}'))
    return new_range

# notes negative_politic
def note_negative_not_posible(kind):
    kind = 'Random' if kind == 'r' else 'Cover'
    c.p(f'[y]NOTE: {kind}-operation[c] has conflicting parameters:')
    c.p('[y]NOTE:[c]   - Negative numbers are not allowed.')
    c.p('[y]NOTE:[c]   - Only "-" operands are used.')
    c.p('[y]NOTE:[c]   - The current result minus the minimum possible value is less than zero.')
    c.p('[y]NOTE:[c]   - The limit has been reached.')
def note_negative_not_satisfy(kind):
    if kind == 'r':
        c.p(f'[y]NOTE: Random-operation[c] does not satisfy [r]the negative numbers policy.[x] Trying again..')
        return True
    if kind == 'c':
        c.p(f'[y]NOTE: Y-pairs for cover-operation[c] does not satisfy [r]the negative numbers policy.')
        return True
    raise Exception(c.z(f'[r]ERROR:[c] unknown kind - {kind}'))
# notes negative_politic - changes
def note_change_operand(new_operand):
    c.p(f'[y]NOTE:[c]   Changing [r]operand by "{new_operand}".')
def note_change_range(side, shift, old_range, new_range):
    old_range, new_range = map(str, old_range), map(str, new_range)
    c.p(f'[y]NOTE:[c]   Changing [r]range {side}:{s.add_sign(shift)}%[c] [x]([c]{"-".join(old_range)} [x]->[c] {"-".join(new_range)}[x])')
# notes extra-cover
def note_length_less_than_req(length, new_sequence):
    c.p(f'[y]NOTE:[c] Not all numbers have been generated yet for possible combinations of units:')
    c.p(f'[y]NOTE:[c]   The specified [y]length in the parameters [y]will be ignored.')
    c.p(f'[y]NOTE:[c]   the specified length in the parameters is {length}.')
    c.p(f'[y]NOTE:[c]   the current length is [y]{len(new_sequence.split())}.')
    return True
def note_length_more_than_req(length, new_sequence):
    c.p(f'[y]NOTE:[c] All combinations were matched:')
    c.p(f'[y]NOTE:[y]   The rest of the sequence will be generated randomly.')
    c.p(f'[y]NOTE:[c]   the current length is [y]{len(new_sequence.split())}.')
    c.p(f'[y]NOTE:[c]   the specified length in the parameters is [y]{length}.')
    return True
def note_cover_no_pairs():
    c.p(f'[y]NOTE:[c] Cover-operation - [y]no y-pairs left[c] for the chain of operations.')
