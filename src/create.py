from src.helpers.colors import *
from src.helpers.fo import Fo as fo
from src.helpers.cmd import Cmd as cmd
import random
import os
from functools import reduce

def create(args):
    if args.kind == 'arithmetic':
        return create_arithmetic(args.first, args.length, args.name)
    if args.kind == 'random':
        return create_random(args.operations, args.length, args.range, args.name)
    if args.kind == 'cover-units':
        return create_cover_units(args.operations, args.range, args.name)
    print(cz(f'[r]unknown "kind" to create the exercise: {args.kind}'))
    exit(1)

# arithmetic
def create_arithmetic(first, length, name):
    print(c_center(cz(f' [y]CREATING (arithmetic-progression) '), 94, '=', 'x'))
    print(cz(f'[g]first element:[c] {first}[g], length: [c]{length}'))
    path = name2path(name) if name else name2path(f'arithmetic_{first}-{length}')
    # data
    operations_kind = 'plus'
    numbers = generate_arithmetic(first, length)
    expresion = get_expresion(numbers, operations_kind)
    total = sum(numbers)
    # save
    data = f'{expresion} ={total}'
    save_file(path, data)
    return path
def generate_arithmetic(first, length):
    first_number = int(first)
    numbers = [first_number]
    for i in range(1, int(length) + 1):
        numbers.append(first_number+i)
    return numbers

# random
def create_random(operations_kind, length, digits_range, name):
    print(c_center(cz(f' [y]CREATING (random type) '), 94, '=', 'x'))
    print(cz(f'[g]length:[c] {length}[g], operations_kind:[c] {operations_kind}[g], digits_range:[c] {digits_range}'))
    path = name2path(name) if name else name2path(f'random-{length}_{operations_kind}_{digits_range}')
    # data
    numbers = generate_random(digits_range, length)
    if operations_kind == 'plus':
        total = sum(numbers)
        expresion = get_expresion(numbers, operations_kind)
    if operations_kind == 'minus':
        numbers.append(sum(numbers))
        numbers.reverse()
        total = numbers.pop(-1)
        expresion = get_expresion(numbers, operations_kind)
    if operations_kind == 'plus-minus':
        expresion = get_expresion(numbers, operations_kind)
        total = eval(expresion)
    if operations_kind == 'plus-minus-roundtrip':
        expresion_plus = get_expresion(numbers, 'plus')
        numbers.reverse()
        total = numbers.pop(0)
        expresion_minus = get_expresion(numbers, 'minus')
        expresion = f'{expresion_plus} - {expresion_minus}'
    # save
    data = f'{expresion} ={total}'
    save_file(path, data)
    return path
def generate_random(digits_range, length):
    numbers = []
    start, end = get_range(digits_range)
    for i in range(1, int(length) + 1):
        numbers.append(random.randint(start, end))
    return numbers

# cover-units
def create_cover_units(operations_kind, digits_range, name):
    print(c_center(cz(f' [y]CREATING (cover-units type) '), 94, '=', 'x'))
    print(cz(f'[g]operations_kind kind:[c] {operations_kind}[g], digits_range:[c] {digits_range}'))
    path = name2path(name) if name else name2path(f'cover-units_{operations_kind}_{digits_range}')
    # data
    numbers = get_cover_units(digits_range)
    if operations_kind == 'plus':
        total = sum(numbers)
        expresion = get_expresion(numbers, operations_kind)
    if operations_kind == 'minus':
        numbers.append(sum(numbers))
        numbers.reverse()
        total = numbers.pop(-1)
        expresion = get_expresion(numbers, operations_kind)
    # TODO: plus-minus
    if operations_kind == 'plus-minus':
        print(cz('[y]TODO:[c] cover-units plus-minus...'))
        exit(1)
    if operations_kind == 'plus-minus-roundtrip':
        expresion_plus = get_expresion(numbers, 'plus')
        numbers.reverse()
        total = numbers.pop(0)
        expresion_minus = get_expresion(numbers, 'minus')
        expresion = f'{expresion_plus} - {expresion_minus}'
    # save
    data = f'{expresion} ={total}'
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
        expresion = ''
        for num in numbers:
            if num == numbers[0]:
                continue
            choice = random.choice(operators)
            summ = summ + num if choice == '+' else summ - num
            if summ < 0:
                choice = '+'
                summ = summ + num
            expresion += f' {choice}{num}'
        return expresion
def get_range(digits_range):
    pre_x, post_x = digits_range.split('-')
    start, end = 10**(len(pre_x)-1), 10**len(post_x)-1
    if start > end:
        print(cz('[y]Note:[c] The first number in the range of digits cannot be longer than the second.'))
        print(cz('[y]Note:[c] The initial value was replaced to "x":'))
        print(cz('[y]Note:[c]    [r]{digits_range}[c] -> [g]x-{post_x}'))
        start = 1
    return (start, end)
def name2path(name):
    base = os.path.basename(name)
    validated_name = os.path.splitext(base)[0]
    return f'./data/{name}.txt'
def save_file(path, data):
    cmd.run('mkdir -p ./data')
    fo.str2txt(data, path)
    print(cz(f'[g]Exercise was created:[c] {path}'))
    print()
