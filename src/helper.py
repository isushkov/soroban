import re
from decimal import Decimal
import ast
import operator

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
            print(cz(f'[r]ERROR:[c] num2str()'))
            print(num)
            exit(1)

def str2num(s):
    return Decimal(str(s))

def do_math(operand, x,y):
    map_operations = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y if y != 0 else (
            print(cz(f'[r]Error:[c] Devision by zero.')),
            sys.exit(1)
        )[1]
    }
    return Decimal(map_operations[operand](x,y))

def safe_eval(expr):
    operators = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.BitXor: operator.xor,
        ast.USub: operator.neg
    }
    def eval_(node):
        if isinstance(node, ast.Num):  # <number>
            return Decimal(str(node.n))
        elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
            return operators[type(node.op)](eval_(node.left), eval_(node.right))
        elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
            return operators[type(node.op)](eval_(node.operand))
        else:
            raise TypeError("Unsupported type: {}".format(type(node)))
    expr = re.sub(r'\s+', '', expr)
    parts = re.findall(r'[-+]?\d+', expr)
    if parts:
        if str2num(parts[0]) < 0:
            expr = '0' + expr
        return eval_(ast.parse(expr, mode='eval').body)
    return 0
