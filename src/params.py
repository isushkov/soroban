import re
import random
from src.helpers.colors import *
from decimal import Decimal, getcontext

# sequences
def parse_params(params, kind):
    sequences = re.split(r'\s+', params.strip())
    parsed_sequences = []
    for seq in sequences:
        is_first_seq = True if seq == sequences[0] else False
        parsed_sequences.append(parse_sequence(seq.strip(), kind, is_first_seq))
    return parsed_sequences
def parse_sequence(sequence, kind, is_first_seq):
    if ':' in sequence:
        required_part, optional_part = sequence.split(':')
    else:
        required_part, optional_part = sequence, ''
    required = parse_required(required_part, kind, is_first_seq)
    optional = parse_optional(optional_part)
    # hooks
    check_precision(required['start_number'], optional['float'])
    check_range_precision(required['range'], optional['float']['precision'])
    return {'required': required, 'optional': optional}

# required
def parse_required(required_str, kind, is_first_seq):
    parts = required_str.split(',')
    expected_lengths = {
        'random': (4 if is_first_seq else 3),
        'cover':  (3 if is_first_seq else 2)
    }
    expected_length = expected_lengths.get(kind, None)
    if len(parts) != expected_length:
        params_error(f'Expected {expected_length} parts, got {len(parts)}: "{required_str}"')
    if not is_first_seq: parts.insert(0, None) # fill start_number
    if kind == 'cover':  parts.append(None)    # fill length
    start_number, operands, value_range, length = parts
    return {
        'start_number': parse_start_number(start_number),
        'operands':     parse_operands(operands),
        'range':        parse_range(value_range),
        'length':       parse_length(length)
    }
def parse_start_number(start_number):
    if start_number is None: return start_number
    if start_number == 'r':  return start_number
    try:
        return int(start_number)
    except ValueError:
        try:
            return float(start_number)
        except ValueError:
            params_error(f'Incorrect start number - "{start_number}".')
def parse_operands(op_str):
    ops = re.findall(r"([+\-*/])(\d*)", op_str)
    operands = {}
    for op, priority in ops:
        operands[op] = int(priority) if priority else 1
    return operands
def parse_range(range_str):
    if range_str.count('-') > 1:
        params_error(f'The range string "{range_str}" contains more than one dash ("-").')
    start, end = map(int, range_str.split('-'))
    if end < 1:
        print(cz('[y]Note:[c] Minimal value for the second number in the range of digits is "1".'))
        print(cz('[y]Note:[c] The initial value was replaced to "1".'))
        end = 1
    if start > end:
        print(cz('[y]Note:[c] The first number in the range of digits cannot be longer than the second.'))
        print(cz('[y]Note:[c] The initial value was replaced to "1".'))
        start = 1
    return (start, end)
def parse_length(length):
    if length is None:
        return length
    try:
        return int(length)
    except ValueError:
        params_error(f'Incorrect length - "{length}".')

# optional
def parse_optional(optional_str):
    options = {}
    options['is_negative']  = True if 'n' in optional_str else False
    options['is_roundtrip'] = True if '<' in optional_str else False
    float_match = re.search(r'\.(\d+)(?:%(\d+))?', optional_str)
    if float_match:
        precision = int(float_match.group(1))
        probability = int(float_match.group(2)) if float_match.group(2) else 10
        options['float'] = {'precision': precision, 'probability': probability}
    else:
        options['float'] = {'precision': False, 'probability': False}
    return options

# hooks
def check_precision(start_number, float_params):
    if start_number == 'r':
        return True
    precision = float_params['precision']
    d_start_number = Decimal(str(start_number))
    try:
        post_decimal_digits = abs(d_start_number.as_tuple().exponent)
    except InvalidOperation:
        post_decimal_digits = 0
    if post_decimal_digits > precision:
        params_error(f'the number of decimal places in start number ({start_number}) exceeds the specified precision ({precision}).')
    return True
def check_range_precision(range_params, precision):
    converter = float if not precision else int
    try:
        converted_range = tuple(converter(x) for x in range_params)
        return converted_range
    except ValueError:
        params_error(f'invalid range: {range_params}')

def params_error(msg):
    print(cz(f'[r]ParamsError:[c] {msg}'))
    exit(1)

def test():
    params_list = [
        "0,+,1-99,100",
        "r,+-,142-9345,5000",
        "34,+2-1,2-13,12",
        "-34,-+2,0-9,5",
        "0,+,1-9,5",
        "0,+,1-9,5:<",
        "0,+,1-9,5:n",
        "0,+,1-9,5:n.2",
        "0,+,1-9,5:n.3%50",
        "0,+,1-9,5:n.4%10<",
        "0,+,1-99,100   +-,142-9345,5000:n.3%50 +2-1,2-13,12:<",
        "0,+,1-99:<     +-,1-999:n.2            *2/,1-9,10"
    ]
    for params in params_list:
        print(cz(f'[y]>>>[c] "{params}"'))
        parsed_params = parse_params(params)
        for seq in parsed_params:
            print(seq)
