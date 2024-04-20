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

def dec(s):
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
        ast.Add: lambda x, y: x + y,
        ast.Sub: lambda x, y: x - y,
        ast.Mult: lambda x, y: x * y,
        ast.Div: lambda x, y: x / y,
        ast.Pow: lambda x, y: x ** y,
        ast.BitXor: lambda x, y: x ^ y,
        ast.USub: lambda x: -x
    }
    def eval_(node):
        if isinstance(node, ast.Num):
            return Decimal(str(node.n))
        elif isinstance(node, ast.BinOp):
            left = eval_(node.left)
            right = eval_(node.right)
            if isinstance(left, Decimal) and isinstance(right, Decimal):
                return operators[type(node.op)](left, right)
            else:
                raise TypeError("Non-decimal operation attempted.")
        elif isinstance(node, ast.UnaryOp):
            operand = eval_(node.operand)
            if isinstance(operand, Decimal):
                return operators[type(node.op)](operand)
            else:
                raise TypeError("Non-decimal unary operation attempted.")
        elif isinstance(node, ast.Expr):
            return eval_(node.value)
        else:
            raise TypeError("Unsupported type: {}".format(type(node)))
    parsed_expr = ast.parse(expr, mode='eval').body
    result = eval_(parsed_expr)
    return result if isinstance(result, Decimal) else Decimal(result)
