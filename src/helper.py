import re
import ast
import operator
from decimal import Decimal, getcontext, ROUND_HALF_UP
import src.helpers.colors as c

def dec(s):
    return Decimal(str(s))
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

def do_math(x, operand, y):
    map_operations = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y if y != 0 else (
            print(c.z(f'[r]Error:[c] Devision by zero.')),
            sys.exit(1)
        )[1]
    }
    return Decimal(map_operations[operand](x,y))

# TODO: "*-", "/-" проверить вычисляется ли это как ожидается:
#                  умножение и деление на отрицательное число
def safe_eval(expression, precision=2):
    def add_unary_pluses_for_not_first_numbers(expression):
        parts = re.split(r'(\d+)', expression, 1)
        if len(parts) < 2:
            return expression
        first_number = parts[1]
        rest = ''.join(parts[2:])
        # добавление '+' перед числами, если перед ними нет оператора или другого числа с оператором
        rest = re.sub(r'(?<=\s)(?![\+\-\*/])(\d+)', r'+\1', rest)
        return parts[0] + first_number + rest

    e = c.z('[r]ERROR - safe_eval():[c]')
    n = c.z('[y]NOTE - safe_eval():[c]')
    # getcontext().prec = precision

    # Удаляем пробельные символы и добавляем один пробел после каждого числа
    expression = re.sub(r'\s+', '', expression)
    expression = re.sub(r'([0-9]*\.?[0-9]+)', r'\1 ', expression).strip()
    # Удалить скобки
    if '(' in expression or ')' in expression:
        print(f"{n} Brackets are removed and all operations are evaluated in sequence.")
        expression = expression.replace('(', '').replace(')', '')
    # Проверка на пустую строку
    if expression == "":
        return Decimal(0)
    # Проверка на допустимость символов: " [0-9].+-*/"
    if not re.match(r'^[\d\.\+\-\*/\s]*$', expression):
        invalid_chars = re.sub(r'[\d\.\+\-\*/\s]', '', expression)
        raise ValueError(f"{m} Invalid characters in the expression: {invalid_chars}")

    # Приведение к общему виду первого числа.
    # ведущий "+": удалять
    expression = re.sub(r'^\+', '', expression)
    # ведущие "*", "/", "*-", "/-": ValueError
    if re.match(r'^[\*/]', expression):
        raise ValueError(f"{e} Expression cannot start with '*' or '/'")

    # Приведение к общему виду не первых чисел:
    # если перед числом нет операнда: добавить "+"
    expression = add_unary_pluses_for_not_first_numbers(expression)
    # после * или / может идти только '-','[0-9]',
    if re.search(r'[*\/](?![0-9-])', expression):
        raise ValueError(f'{e} after "*" or "/", only "-" or digits can go.')
    # "*+2.5" > "*2.5"
    expression = re.sub(r'\*\+([0-9]*\.?[0-9]+)', r'*\1', expression)
    # "/+2.5" > "/2.5"
    expression = re.sub(r'/\+([0-9]*\.?[0-9]+)', r'/\1', expression)

    # Синтаксический разбор и вычисление выражения
    try:
        tree = ast.parse(expression, mode='eval')
    except SyntaxError:
        raise ValueError("Invalid syntax in expression.")

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
                if right == Decimal(0):
                    raise ZeroDivisionError(f"{e} Division by zero is not allowed.")
                return left / right
        elif isinstance(node, ast.UnaryOp):
            operand = eval_(node.operand)
            if isinstance(node.op, ast.UAdd):
                return operand
            elif isinstance(node.op, ast.USub):
                return -operand
        elif isinstance(node, ast.Num):
            return Decimal(str(node.n))
        else:
            raise TypeError(f"{e} Unsupported type")

    result = eval_(tree)
    if result == result.to_integral_value():
        return result.quantize(Decimal('1'))
    return result.quantize(Decimal('1.' + '0' * precision), rounding=ROUND_HALF_UP)
