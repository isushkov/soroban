import re
import random
from src.helpers.colors import *

# sequences
def parse_params(params):
    sequences = re.split(r'\s+', params.strip())
    parsed_sequences = []
    for seq in sequences:
        is_first_seq = True if seq == sequences[0] else False
        parsed_sequences.append(parse_sequence(seq.strip(), is_first_seq))
    return parsed_sequences
def parse_sequence(sequence, is_first_seq):
    if ':' in sequence:
        required_part, optional_part = sequence.split(':')
    else:
        required_part, optional_part = sequence, ''
    required = parse_required(required_part, is_first_seq)
    optional = parse_optional(optional_part)
    return required, optional

# required
def parse_required(required_str, is_first_seq):
    parts = required_str.split(',')
    if is_first_seq:
        if len(parts) == 4:
            start_number, operands, value_range, length = parts
        elif len(parts) == 3:
            start_number, operands, value_range = parts
            length = 0
        else:
            print(cz(f'[r]Invalid params for required options:[c] "{required_str}"'))
            exit(1)
    else:
        start_number = 0
        if len(parts) == 3:
            operands, value_range, length = parts
        elif len(parts) == 2:
            operands, value_range = parts
            length = 0
        else:
            print(cz(f'[r]Invalid params for required options:[c] "{required_str}"'))
            exit(1)
    value_range = parse_range(value_range)
    start_number = parse_start_number(start_number, value_range)
    operands = parse_operands(operands)
    length = int(length)
    return {
        'start_number': start_number,
        'operands': operands,
        'range': value_range,
        'length': length
    }
def parse_range(range_str):
    print(range_str)
    start, end = map(int, range_str.split('-'))
    return (start, end)
def parse_start_number(sn_str, value_range):
    if sn_str == 'r':
        return random.uniform(*value_range)
    return float(sn_str)
def parse_operands(op_str):
    ops = re.findall(r"([+\-*/])(\d*)", op_str)
    operands = {}
    for op, priority in ops:
        operands[op] = int(priority) if priority else 1
    return operands

# optional
def parse_optional(optional_str):
    options = {}
    if 'n' in optional_str:
        options['allow_negative'] = True
    if '<' in optional_str:
        options['roundtrip'] = True
    float_match = re.search(r'\.(\d+)%?(\d+)?', optional_str)
    if float_match:
        precision = int(float_match.group(1))
        probability = int(float_match.group(2)) if float_match.group(2) else 10
        options['float'] = {'precision': precision, 'probability': probability}
    return options

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
