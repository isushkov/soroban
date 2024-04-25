import re
import random
import src.helper as h
import src.helpers.colors as c

# common
def parse_params(params):
    sequences = re.split(r'\s+', params.strip())
    params = []
    if len(sequences) < 2:
        params_error('params', ' '.join(sequences), 'a [y]<start-number>[c] and at least one [y]<sequence>[c] must be specified')
    # start_param
    start_param = sequences.pop(0)
    params.append(parse_start_param(start_param.strip()))
    # sequences
    for seq in sequences:
        params.append(parse_sequence(seq.strip()))
    return params
def parse_start_param(start_param):
    validate(start_param, r'^s(-?\d+(\.\d+)?|r)$', 'start-number')
    return start_param[1:]
def parse_sequence(sequence):
    kind, sequence = parse_kind(sequence)
    semicolons = sequence.count(':')
    if semicolons > 1:
        params_error('sequence', sequence)
    req, opt = (sequence.split(':')) if semicolons == 1 else (sequence, '')
    if kind == 'p': required, optional = parse_sequence_progression(req, opt)
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
    if not kind in ['p', 'r', 'c']:
        params_error('kind', kind, 'can only be "a", "r", "c"')
    return kind, sequence

# progression
def parse_sequence_progression(req, opt):
    # required
    if req.count(',') != 1:
        params_error('required', req)
    delta, length = req.split(',')
    if len(delta) < 2:
        params_error('required', req)
    operand = delta[0]
    diff = validate(delta[1:], r'^[1-9]\d*(\.\d+)?$', 'diff')
    required = {
        'operands': { validate(operand, r'^[+-/*]$', 'operand', 'progression can have only one operand'): 1 },
        'range': (diff, diff),
        'length': validate(length, r'^[1-9]\d*$', 'length')
    }
    # optional
    optional = {
        'negative_allowed': parse_negative(opt),
        'decimal': { 'precision': False, 'probability': False },
        'roundtrip': parse_roundtrip(opt)
    }
    validate_optional(opt, ['n', '<'])
    return required, optional

# random/cover
def parse_sequence_randcover(kind, req, opt):
    # required
    commas = req.count(',')
    if kind == 'r':
        if commas != 2:
            params_error('required', req)
        operands_param, range_param, length = req.split(',')
        length = validate(length, r'^[1-9]\d*$', 'length')
    if kind == 'c':
        if commas == 1:
            operands_param, range_param = req.split(',')
            length = False
        elif commas == 2:
            operands_param, range_param, length = req.split(',')
            length = validate(length, r'^[1-9]\d*$', 'length')
        else:
            params_error('required', req)
    required = {
        'operands': parse_operands(operands_param),
        'range': parse_range(range_param),
        'length': length
    }
    # optional
    decimal, decimal_str = parse_decimal(opt)
    optional = {
        'negative_allowed': parse_negative(opt),
        'decimal': decimal,
        'roundtrip': parse_roundtrip(opt)
    }
    validate_optional(opt, ['n', decimal_str, '<'])
    return required, optional

# shared
def parse_operands(operands_param):
    # проверка на общий вид без учета уникальности операндов
    validate(operands_param, r'^[+\-*/]([1-9]\d*)?([+\-*/]([1-9]\d*)?)*$', 'operands')
    ops = re.findall(r"([+\-*/])(\d*)", operands_param, re.IGNORECASE)
    operands = {}
    for op, priority in ops:
        if op in operands:
            params_error('operands', operands, f'duplicate operator "{op}"')
        operands[op] = int(priority) if priority else 1
    return operands
def parse_range(range_param):
    validate(range_param, r'^[1-9]\d*-[1-9]\d*$', 'range')
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
    opt_orig = opt
    for v in values:
        opt = opt.replace(v, '')
    if opt:
        params_error('optional', opt_orig, f'unknown chears "{opt}"')
def validate(string, pattern, errtitle, errmsg=False):
    if not bool(re.fullmatch(pattern, string, re.IGNORECASE)):
        params_error(errtitle, string, errmsg)
    return string
def params_error(errtitle, errval, errmsg=False):
    message = '' if not errmsg else f'{errmsg} - '
    c.p(f'[r]ParamsError - Invalid <{errtitle}>:[c] {message}got [r]"{errval}"[c].')
    exit(2)

# params2basename
def params2basename(params):
    names = []
    for seq_params in params:
        kind = seq_params['kind']
        names.append(seq_params2seq_name(kind, seq_params))
    return 'x'+params[0]+'_'+'_'.join(names)
def seq_params2seq_name(kind, seq_params):
    m = {'+':'A', '-':'S', '*':'M', '/':'D'}
    operands = ''.join([f'{m[k]}{v}' for k,v in seq_params['required']['operands'].items()])
    range_params = 'x'.join(str(i) for i in seq_params['required']['range'])
    length = int(seq_params['required']['length'])
    decimal_params = seq_params['optional']['decimal']
    precision = 1 if decimal_params['precision'] else 0
    probability = 1 if decimal_params['probability'] else 0
    negative = f"{1 if seq_params['optional']['negative_allowed'] else 0}"
    decimal = f'{precision}x{probability}'
    roundtrip = f"{1 if seq_params['optional']['roundtrip'] else 0}"
    return f'{kind}{operands}g{range_params}l{length}-n{negative}d{decimal}r{roundtrip}'
