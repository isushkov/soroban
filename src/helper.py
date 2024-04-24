import re
import ast
import operator
from decimal import Decimal, getcontext, ROUND_HALF_UP
import src.helpers.colors as c

def dec(s, precision=2):
    precision = f'0.{"0" * precision}'
    return Decimal(str(s)).quantize(Decimal(precision), rounding=ROUND_HALF_UP)
def num2str(num):
    if isinstance(num, Decimal):
        if num == num.to_integral_value():
            return str(num.quantize(Decimal('1')))
        return str(num)
    try:
        return str(int(num))
    except ValueError:
        try:
            return str(num)
        except ValueError:
            print(c.z(f'[r]ERROR:[c] num2str(): {num}'))
            exit(1)
def do_math(x, operand, y, precision=2):
    map_operations = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y if y != 0 else (
            print(c.z(f'[r]Error:[c] Devision by zero.')),
            sys.exit(1)
        )[1]
    }
    return dec(map_operations[operand](x,y), precision)

def add_sign(num_str):
    num_str = num2str(num_str)
    num_str = num_str.strip()
    if not num_str:
        return num_str
    if num_str[0].isdigit():
        return '+' + num_str
    if num_str[0] in '+-':
        return num_str
    raise ValueError(c.z(f'[r]ERROR:[c] add_sign(): {num_str}'))
def del_sign(num_str):
    num_str = num2str(num_str)
    num_str = num_str.strip()
    if not num_str:
        return num_str
    if num_str[0].isdigit():
        return num_str
    if num_str[0] in '+-':
        return num_str[1:]
    raise ValueError(c.z(f'[r]ERROR:[c] del_sign(): {num_str}'))


# TODO: "*-", "/-" проверить вычисляется ли это как ожидается:
#                  умножение и деление на отрицательное число
def safe_eval(sequence, precision=2):
    e = c.z('[r]ERROR:[c]')
    n = c.z('[y]NOTE:[c]')
    sequence = validate_sequence(sequence, 'safe_eval()', exit_policy=1)
    if not sequence:
        return dec(0, precision)
    # Синтаксический разбор и вычисление выражения
    try:
        tree = ast.parse(sequence, mode='eval')
    except SyntaxError:
        raise ValueError("Invalid syntax in sequence.")
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
                if right == dec(0, precision):
                    raise ZeroDivisionError(f"{e} Division by zero is not allowed.")
                return left / right
        elif isinstance(node, ast.UnaryOp):
            operand = eval_(node.operand)
            if isinstance(node.op, ast.UAdd):
                return operand
            elif isinstance(node.op, ast.USub):
                return -operand
        elif isinstance(node, ast.Num):
            return dec(str(node.n), precision)
        else:
            raise TypeError(f"{e} Unsupported type")
    return dec(eval_(tree), precision)

def split_operation(operation):
    match = re.match(r'([*/+-]*)\s*(-?\d+(?:\.\d+)?)', operation)
    if not match:
        return '', operation
    operand, number_str = match.groups()
    return operand, number_str
# exit_policy:
#     0 - exit: no,  traceback: replace by note
#     1 - exit: yes, traceback: yes
#     2 - exit: yes, traceback: replace by note
def validate_sequence(sequence, pfx=False, exit_policy=0):
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
    if exit_policy == 1: raise ValueError(msg)
    if exit_policy == 2: print(msg); exit(2)
