import re
import random
from src.helper import *
from src.helpers.colors import *


# common
def parse_params(params):
    sequences = re.split(r'\s+', params.strip())
    params = []
    if len(sequences) < 2:
        msg = f'A [y]<start-number>[c] and at least one [y]<sequence>[c] must be specified - got [r]{sequences}[c].'
        params_error(msg)
    # start_param
    start_param = sequences.pop(0)
    params.append(parse_start_param(start_param.strip()))
    # sequences
    for seq in sequences:
        params.append(parse_sequence(seq.strip()))
    return params
def parse_start_param(start_param):
    msg = f'Invalid [y]<start-number>[c] - got [r]{start_param}[c].'
    validate(start_param, r'^s(-?\d+(\.\d+)?|r)$', msg)
    return start_param[1:]
def parse_sequence(sequence):
    kind, sequence = parse_kind(sequence)
    semicolons = sequence.count(':')
    if semicolons > 1:
        msg = f'Invalid [y]<sequence>[c] - got [r]{sequence}[c].'
        params_error(msg)
    req, opt = (sequence.split(':')) if semicolons == 1 else (sequence, '')
    if kind == 'a': required, optional = parse_sequence_arithmetic(req, opt)
    if kind == 'r': required, optional = parse_sequence_randcover('r', req, opt)
    if kind == 'c': required, optional = parse_sequence_randcover('c', req, opt)
    return {
        'kind': kind,
        'required': required,
        'optional': optional
    }
def parse_kind(sequence):
    kind = sequence[0]
    sequence = sequence[1:]
    if not kind in ['a', 'r', 'c']:
        params_error(f'[y]<kind>[c] can only be "a", "r", "c" - got [r]{kind}[c]')
    return kind, sequence

# arithmetic
def parse_sequence_arithmetic(req, opt):
    # required
    if req.count(',') != 1:
        params_error(f'Invalid [y]<required>[c] - got [r]{req}[c]')
    diff, length = req.split(',')
    required = {
        'diff': validate(diff, r'^-?[1-9]\d*(\.\d+)?$', f'Invalid [y]<diff>[c] - got [r]{diff}[c]'),
        'length': validate(length, r'^[1-9]\d*$', f'Invalid [y]<length>[c] - got [r]{length}[c]')
    }
    # optional
    optional = {'roundtrip': parse_roundtrip(opt)}
    validate_optional(opt, ['<'])
    return required, optional

# random/cover
def parse_sequence_randcover(kind, req, opt):
    # required
    msg = f'Invalid [y]<required>[c] - got [r]{req}[c].'
    commas = req.count(',')
    if kind == 'r':
        if commas != 2:
            params_error(msg)
        operands_param, range_param, length = req.split(',')
        length = validate(length, r'^[1-9]\d*$', f'Invalid [y]<length>[c] - got [r]{length}[c]')
    if kind == 'c':
        if commas == 1:
            operands_param, range_param = req.split(',')
            length = False
        elif commas == 2:
            operands_param, range_param, length = req.split(',')
            length = validate(length, r'^[1-9]\d*$', f'Invalid [y]<length>[c] - got [r]{length}[c]')
        else:
            params_error(msg)
    required = {
        'operands': parse_operands(operands_param),
        'range': parse_range(range_param),
        'length': length
    }
    # optional
    decimal, decimal_str = parse_decimal(opt)
    optional = {
        'allow_negative': parse_negative(opt),
        'decimal': decimal,
        'roundtrip': parse_roundtrip(opt)
    }
    validate_optional(opt, ['n', decimal_str, '<'])
    return required, optional

# shared
def parse_operands(operands_param):
    # проверка на общий вид без учета уникальности операндов
    msg = f'Invalid [y]<operands>[c] - got [r]{operands_param}[c].'
    validate(operands_param, r'^[+\-*/]([1-9]\d*)?([+\-*/]([1-9]\d*)?)*$', msg)
    ops = re.findall(r"([+\-*/])(\d*)", operands_param, re.IGNORECASE)
    operands = {}
    for op, priority in ops:
        if op in operands:
            params_error(f'Invalid <operands> - duplicate operator "{op}".')
        operands[op] = int(priority) if priority else 1
    return operands
def parse_range(range_param):
    msg = f'Invalid [y]<range>[c] - got [r]{range_param}[c].'
    validate(range_param, r'^[1-9]\d*-[1-9]\d*$', msg)
    return range_param.split('-')
def parse_negative(opt):
    return True if 'n' in opt else False
def parse_decimal(opt):
    float_match = re.search(r'\.([1-9]\d*)(?:%([1-9][0-9]?|100))?', opt, re.IGNORECASE)
    if float_match:
        precision = int(float_match.group(1))
        probability = int(float_match.group(2)) if float_match.group(2) else 10
        decimal = {'precision': precision, 'probability': probability}
        decimal_str = float_match.group(0)
    else:
        decimal = {'precision': False, 'probability': False}
        decimal_str = ''
    return decimal, decimal_str
def parse_roundtrip(opt):
    return True if '<' in opt else False
def validate_optional(opt, values):
    for v in values:
        opt = opt.replace(v, '')
    if opt:
        params_error(f'Invalid [y]<optional>[c] - got [r]{opt}[c]')
def validate(string, pattern, msg):
    if not bool(re.fullmatch(pattern, string, re.IGNORECASE)):
        params_error(msg)
    return string
def params_error(msg):
    print(cz(f'[r]ParamsError:[c] {msg}'))
    exit(2)
