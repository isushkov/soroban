import random
import src.helpers.fexit
from src.helpers.colors import *
from src.helpers.fo import Fo as fo
from src.helpers.cmd import Cmd as cmd

# common
def get_operation_char(operations):
    if operations == 'plus':  return '+'
    if operations == 'minus': return '-'
    # TODO: unknown operations
    fexit('TODO: unknown operations...')
def get_sequence(numbers, operation_char):
    return f' {operation_char} '.join(str(addition) for addition in numbers)
def get_total(numbers, operation_char):
    if operation_char == '+':
        return sum(numbers)
    if operation_char == '-':
        first_element = numbers[0]
        rest_elements_sum = sum(numbers[1:])
        return first_element - rest_elements_sum
def save_file(name, data):
    cmd.run('mkdir -p ./data')
    path = f'data/{name}.txt'
    fo.str2txt(data, path)
    print(cz(f'[g]Exercise was created:[c] {path}'))

# arithmetic
def create_arithmetic(first, length, name):
    print(c_center(cz(f' [y]CREATING (arithmetic-progression type) '), 94, '=', 'x'))
    print(cz(f'[g]first element:[c] {first}[g], length: [c]{length}'))
    name = name if name else f'arithmetic_{first}-{length}'
    operation_char = '+'
    # numbers
    numbers = generate_arithmetic(first, length)
    sequence = get_sequence(numbers, operation_char)
    total = get_total(numbers, operation_char)
    save_file(name, f'{sequence} = {total}')
    print()
    return name
def generate_arithmetic(first, length):
    first_number = int(first)
    numbers = [first_number]
    for i in range(1, int(length) + 1):
        numbers.append(first_number+i)
    return numbers
# random
def create_random(operations, length, digits_range, name):
    print(c_center(cz(f' [y]CREATING (random type) '), 94, '=', 'x'))
    print(cz(f'[g]length:[c] {length}[g], operations:[c] {operations}[g], digits_range:[c] {digits_range}'))
    name = name if name else f'random-{length}_{operations}_{digits_range}'
    operation_char = get_operation_char(operations)
    # numbers
    numbers = generate_random(digits_range, length)
    sequence = get_sequence(numbers, operation_char)
    total = get_total(numbers, operation_char)
    save_file(name, f'{sequence} = {total}')
    print()
    return name
def generate_random(digits_range, length):
    numbers = []
    start, end = get_range(digits_range)
    for i in range(1, int(length) + 1):
        numbers.append(random.randint(start, end))
    return numbers

# cover-units
def create_cover_units(operations, digits_range, name):
    print(c_center(cz(f' [y]CREATING (cover-units type) '), 94, '=', 'x'))
    print(cz(f'[g]operations:[c] {operations}[g], digits_range:[c] {digits_range}'))
    name = name if name else f'cover-units_{operations}_{digits_range}'
    operation_char = get_operation_char(operations)
    # numbers
    numbers = generate_cover_units(digits_range, operation_char)
    sequence = get_sequence(numbers, operation_char)
    total = get_total(numbers, operation_char)
    save_file(name, f'{sequence} = {total}')
    print()
    return name
# TODO: generate_cover for all digit
# TODO: '-' убедиться что не уходит в отрицательные при любых digits_range
# TODO: '-' сделать чтобы сумма всегда была 0
def generate_cover_units(digits_range, operation_char):
    if operation_char == '+':
        first_number = 0
    else:
        fexit('TODO: unknown operations...')
    result = [first_number]
    all_combinations = {(x, y) for x in range(0, 10) for y in range(1, 10)}
    while all_combinations:
        x,y, all_combinations = get_units(first_number, all_combinations)
        second_number = generate_second_number(digits_range, y)
        result.append(second_number)
        if operation_char == '+':
            first_number += second_number
        else:
            fexit('TODO: unknown operations...')
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

def get_range(digits_range):
    pre_x, post_x = digits_range.split('-')
    start, end = 10**(len(pre_x)-1), 10**len(post_x)-1
    if start > end:
        print(cz('[y]Note:[c] The first number in the range of digits cannot be longer than the second.'))
        print(cz('[y]Note:[c] The initial value was replaced to "x":'))
        print(cz('[y]Note:[c]    [r]{digits_range}[c] -> [g]x-{post_x}'))
        start = 1
    return (start, end)
