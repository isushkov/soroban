import re
import ast
# src/helpers
import src.helpers.colors as c

# str/num
def tonum(val, rnd=None):
    max_rnd = 6
    if not isinstance(val, (str, int, float)):
        raise ValueError(c.z(f'[r]ERROR - tonum():[c] unknown type {type(val)} ({val}).'))
    if isinstance(val, str):
        try:
            val = float(val)
        except ValueError:
            raise ValueError(c.z(f'[r]ERROR - tonum():[c] Cannot convert {val} to a number.'))
    # определение необходимости округления
    if isinstance(val, float):
        current_precision = len(str(val).split('.')[-1])
        # округление, если rnd задан
        if rnd is not None:
            multiplier = 10 ** rnd
            val = int(val * multiplier) / multiplier
        # max_rnd, если rnd не задан
        elif current_precision > max_rnd:
            multiplier = 10 ** max_rnd
            val = int(val * multiplier) / multiplier
    # преобразование float в int, если результат является целым числом
    if isinstance(val, float) and val.is_integer():
        return int(val)
    return val
# num/str
def tostr(val, rnd=None):
    if not isinstance(val, (str, int, float)):
        raise ValueError(c.z(f'[r]ERROR - tostr():[c] unknown type {type(val)} ({val}).'))
    return str(tonum(val, rnd))
# num/num
def do_math(x, operand, y, rnd=None):
    x,y = tonum(x), tonum(y)
    map_operations = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y
    }
    return tonum(map_operations[operand](x,y), rnd)
# TODO: fix setrecursionlimit
def safe_eval(sequence, rnd=2):
    e = c.z('[r]ERROR:[c]')
    n = c.z('[y]NOTE:[c]')
    sequence = validate_sequence(sequence, 'safe_eval()', exit_policy=1)
    if not sequence:
        return tonum(0, rnd)
    try:
        tree = ast.parse(sequence, mode='eval')
    except SyntaxError:
        raise ValueError(c.z(f'{e} Invalid syntax in sequence.'))
    def eval_(node):
        if isinstance(node, ast.Expression):
            return eval_(node.body)
        elif isinstance(node, ast.BinOp):
            left = eval_(node.left)
            right = eval_(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                if right == tonum(0, rnd):
                    raise ZeroDivisionError(c.z(f'{e} Division by zero is not allowed.'))
                return left / right
        elif isinstance(node, ast.UnaryOp):
            operand = eval_(node.operand)
            if isinstance(node.op, ast.UAdd):
                return operand
            elif isinstance(node.op, ast.USub):
                return -operand
        elif isinstance(node, ast.Num):
            return tonum(str(node.n), rnd)
        else:
            raise TypeError(c.z(f'{e} Unsupported type'))
    return tonum(eval_(tree), rnd)

# seq/seq
def add_sign(val):
    val = tostr(val)
    if val[0].isdigit(): return '+' + val
    if val[0] in '+-':   return val
    raise ValueError(c.z(f'[r]ERROR - add_sign():[c] {val}'))
def del_sign(val):
    val = tostr(val)
    if val[0].isdigit(): return val
    if val[0] in '+-':   return val[1:]
    raise ValueError(c.z(f'[r]ERROR:[c] del_sign(): {val}'))
def split_operation(operation):
    operation = re.sub(r'\s+', '', operation)
    match = re.match(r'([*/+-]*)(\d+(?:\.\d+)?)', operation)
    if not match:
        return '', operation
    return match.groups()
def validate_sequence(sequence, pfx=False, exit_policy=0):
    """exit_policy:
       0 - exit: no,  traceback: replace by note
       1 - exit: yes, traceback: yes
       2 - exit: yes, traceback: replace by note
    """
    pfx = f' - {pfx}' if pfx else ''
    e = c.z(f'[r]ERROR{pfx}:[c]')
    n = c.z(f'[y]NOTE{pfx}:[c]')
    def add_unary_pluses_for_not_first_numbers(sequence):
        parts = re.split(r'(\d+)', sequence, 1)
        if len(parts) < 2:
            return sequence
        first_number = parts[1]
        rest = ''.join(parts[2:])
        # добавление '+' перед числами, если перед ними нет оператора или другого числа с оператором
        rest = re.sub(r'(?<=\s)(?![\+\-\*/])(\d+)', r'+\1', rest)
        return parts[0] + first_number + rest
    # Удаляем пробельные символы и добавляем один пробел после каждого числа
    sequence = re.sub(r'\s+', '', sequence)
    sequence = re.sub(r'([0-9]*\.?[0-9]+)', r'\1 ', sequence).strip()
    # Удалить скобки
    if '(' in sequence or ')' in sequence:
        print(f'{n} Brackets are removed and all operations will be performed one by one')
        sequence = sequence.replace('(', '').replace(')', '')
    # Проверка на пустую строку
    if sequence == '':
        print(f'{n} is empty.')
        return False
    # Проверка на допустимые символы: " [0-9].+-*/"
    if not re.match(r'^[\d\.\+\-\*/\s]*$', sequence):
        invalid_chars = re.sub(r'[\d\.\+\-\*/\s]', '', sequence)
        apply_exit_policy(exit_policy, f"{e} Invalid characters: {invalid_chars}")
    # Приведение к общему виду первого числа.
    # ведущий "+": удалять
    sequence = re.sub(r'^\+', '', sequence)
    # ведущие "*", "/", "*-", "/-": ValueError
    if re.match(r'^[\*/]', sequence):
        apply_exit_policy(exit_policy, f"{e} cannot start with '*' or '/'")
    # Приведение к общему виду не первых чисел:
    # если перед числом нет операнда: добавить "+"
    sequence = add_unary_pluses_for_not_first_numbers(sequence)
    # после * или / может идти только '-','[0-9]',
    if re.search(r'[*\/](?![0-9-])', sequence):
        apply_exit_policy(exit_policy, f'{e} after "*" or "/", only "-", "(", ")" or digits can go.')
    # "*+2.5" > "*2.5"
    sequence = re.sub(r'\*\+([0-9]*\.?[0-9]+)', r'*\1', sequence)
    # "/+2.5" > "/2.5"
    sequence = re.sub(r'/\+([0-9]*\.?[0-9]+)', r'/\1', sequence)
    # удалить не значимые нули
    sequence = re.sub(r'\+0(?!\.)', '', sequence)
    sequence = re.sub(r'-0(?!\.)', '', sequence)
    return sequence
def apply_exit_policy(exit_policy, msg):
    if exit_policy == 0: print(msg)
    if exit_policy == 1: raise ValueError(c.z(msg))
    if exit_policy == 2: print(msg); exit(2)

# analyze
def maxsum(start_number, ops):
    res, max_res = start_number, 0
    for op in ops:
        operand, number = split_operation(op)
        res = do_math(res, operand, tonum(number))
        if res > max_res: max_res = res
    return max_res
