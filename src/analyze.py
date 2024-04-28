import re
import shutil
from collections import Counter
import src.sequence as s
import src.helpers.colors as c
import src.helpers.fo as fo

# density:
def analyze(path):
    print(c.center(c.z(f' [y]ANALYZE {path} '), 94, '=', 'x'))
    # validation
    sequence, total = fo.txt2str(path).split('=')
    sequence = s.validate_sequence(sequence, 'analyze sequence', exit_policy=2)
    total_is_valid = validate_total(total)
    # density
    #   - найти самую длинную дробную чать, посчитать количество знаков.
    #   - умножить каждое число на 10^max_f, чтобы избавиться от дробей.
    #   - посчитать density.
    min_i, max_i, min_f, max_f = find_min_max_digits(sequence)
    density_pos, density_neg = get_density(sequence, max_f)
    # tables: сместить названия таблиц на 10^(-max_fract_digits).
    tables_fract = get_tables(max_f, density_pos, density_neg, is_fract=True)
    tables_integ = get_tables(max_i, density_pos, density_neg, is_fract=False)
    tables_final = [
        get_table_total(density_pos, density_neg),
        get_table_info(sequence, min_i,max_i,min_f,max_f, total, total_is_valid)
    ]
    # render
    tab, sep = ' '*3, ' '*3
    width, _ = shutil.get_terminal_size()
    r_fract  = render_tables(sep, tables_fract, width, tab=tab)
    r_integ  = render_tables(sep, tables_integ, width, tab=tab)
    r_final  = render_tables(sep, tables_final, width, tab=tab)
    width_tables = len(c.remove_colors(r_integ.splitlines()[0])) - len(sep)
    r_header  = render_header(sep, width_tables)
    r_sepline = render_sepline(sep, width_tables)
    print(r_header)
    print(r_fract);
    if r_fract: print(r_sepline)
    print(r_integ)
    if r_fract: print(r_sepline)
    print(r_final)

# validate
def validate_total(total):
    total = s.validate_sequence(total, 'analyze total', exit_policy=1)
    msg = c.z(f"[y]NOTE:[c] total is invalid - [r]'{total}'")
    if not total:
        print(msg); return False
    if not bool(re.match(r'^-?\d+(\.\d+)?$', total)):
        print(msg); return False
    return True

# density
def find_min_max_digits(sequence):
    numbers = re.findall(r'[+\-*/]?(\d+(\.\d+)?)', sequence)
    min_i, min_f, max_i, max_f = float('inf'), float('inf'), 0, 0
    for number, decimal_part in numbers:
        if '.' in number:
            integ_part, fract_part = number.split('.')
            min_f = min(min_f, len(fract_part))
            max_f = max(max_f, len(fract_part))
        else:
            integ_part = number
        min_i = min(min_i, len(integ_part))
        max_i = max(max_i, len(integ_part))
    if min_f == float('inf'): min_f = 0
    if min_f == float('inf'): min_i = 0
    return min_i, max_i, min_f, max_f
def get_density(sequence, max_f):
    density_pos = {}
    density_neg = {}
    operations = sequence.split()
    # для каждой пары чисел
    total = s.tonum(operations[0])
    for operation in operations[1:]:
        operand, number_str = s.split_operation(operation)
        # TODO: * / *- /-
        if operand not in ['+', '-']: c.todo(f'density for "{operand}"')
        # сдвигаем число право на максимальное количество запятых
        number = s.tonum(number_str) * (10 ** max_f)
        if operand == '+': density = density_pos
        if operand == '-': density = density_neg
        # для каждого разряда. всего разрядов - длина второго слогаемого
        for digit in range(len(str(number))):
            d_density = density.get(digit, Counter())
            density[digit] = upd_density(d_density, digit, total, number)
        # next
        if operand == '+': density_pos = density
        if operand == '-': density_neg = density
        total = s.do_math(total, operand, number)
    return density_pos, density_neg
def upd_density(d_density, digit, total, number):
    y,x = get_yx(total, number, digit)
    d_density[(y,x)] += 1 # сколько раз встретилась комбинация
    return d_density
def get_yx(total, number, digit):
    divisor = 10 ** digit
    y = (total // divisor) % 10
    x = (number // divisor) % 10
    return y,x

# tables
def get_tables(max_d, density_pos, density_neg, is_fract=False):
    tables = []
    for digit in range(0, max_d):
        tables.append(get_table(digit, density_pos.get(digit), density_neg.get(digit), is_fract))
    return tables
def get_table_total(density_pos, density_neg):
    density_total_pos = Counter()
    density_total_neg = Counter()
    for counter in density_pos.values():
        density_total_pos += counter
    for counter in density_neg.values():
        density_total_neg += counter
    return get_table('total', density_total_pos, density_total_neg)

def get_table(digit, density_pos, density_neg, is_fract=False):
    table = []
    # title
    if digit == 'total':
        title = '──[ TOTAL ]──'
    else:
        if is_fract:
            title = f'──[ 0.1^{digit+1} ]──'
        else:
            shift2title = {0:'──[ Units ]──', 1:'──[ Tens ]───', 2:'[ Hundreds ]─'}
            title = shift2title.get(digit, f'──[ 10 ^{digit} ]──')
    table.append(c.z(f'[x]   ┌───{title}───┐     '))
    table.append(c.z( '[x]┌───┴─[ - ]─┬───┬─[ + ]─┴───┐'))
    # rows
    for y in range(9, -1, -1):
        row_middle = f' │ {y} │ '
        row_left   = get_density_row(y, density_neg, range(9, 0, -1))
        row_right  = get_density_row(y, density_pos, range(1, 10))
        table.append(c.z(f"[x]│ [c]{row_left}[x]{row_middle}[c]{row_right}[x] │"))
    # footer
    table.append(c.z('[x]├───────────┼───┼───────────┤'))
    table.append(c.z('[x]└─987654321─┘   └─123456789─┘'))
    return table
def get_density_row(y, density, rng):
    row = ''
    for x in rng:
        count = density.get((y, x), 0) if density else 0
        row += get_count_str(count)
    return row
def get_count_str(count):
    if count == 0: return c.z('[c] ')
    if count == 1: return c.z('[g]x')
    if count <= 9: return c.z(f'[y]{count}')
    if count > 9: return c.z('[r]*')
    return str(count)
# info
def get_table_info(sequence, min_i,max_i,min_f,max_f, total, total_is_valid, spoilers=False):
    d_min = '.' if min_f else ''
    d_max = '.' if max_f else ''
    start_number      = sequence.split()[0]
    count_numbers     = len(sequence.split())
    existed_operands  = ' '.join(list(set(s.split_operation(op)[0] for op in sequence.split()))).strip()
    decimal_exist     = render_yn(max_f)
    negative_results  = render_yn(s.apply(lambda total: total < 0, sequence))
    range_numbers     = f"{'x'*min_i}{d_min}{'x'*min_f}[x]>[c]{'x'*max_i}{d_max}{'x'*max_f}"
    range_results     = render_range_results(s.apply(get_range_results, sequence), spoilers)
    total_provided    = render_yn(total)
    total_valid       = render_yn(total_is_valid)
    total_correct     = render_yn(s.tonum(total) == s.safe_eval(sequence))
    return [
        c.z(f''),
        c.z(f''),
        c.z(f'[x]Start number:     [c]{start_number}'),
        c.z(f'[x]Count numbers:    [c]{count_numbers}'),
        c.z(f'[x]Existed operands: [c]{existed_operands}'),
        c.z(f'[x]Decimal exist:    [c]{decimal_exist}'),
        c.z(f'[x]Negative results: [c]{negative_results}'),
        c.z(f'[x]Range numbers:    [c]{range_numbers}'),
        c.z(f'[x]Range results:    [c]{range_results}'),
        c.z(f'[x]Total provided:   [c]{total_provided}'),
        c.z(f'[x]Total valid:      [c]{total_valid}'),
        c.z(f'[x]Total correct:    [c]{total_correct}'),
        c.z(f'')
    ]
def render_yn(value):
    return 'Yes' if value else 'No'
def render_range_results(range_results, spoilers):
    min_result, max_result = range_results
    if not spoilers:
        min_result, max_result = blur(min_result), blur(max_result)
    return c.z(f'{min_result}[x]>[c]{max_result}')
def blur(number):
    return re.sub(r'\d', 'x', str(number))
def get_range_results(total, range_results=(0,0)):
    min_result, max_result = range_results
    if total < min_result: min_result = total
    if total > max_result: max_result = total
    return (min_result, max_result)
# render
def render_tables(sep, tables, term_width, tab=' '*3):
    if not tables:
        return ''
    # Определяем максимальное количество строк среди всех таблиц
    max_rows = max(len(table) for table in tables)
    # Ширина одной таблицы с учетом сепаратора
    table_width = max(len(c.remove_colors(table[0])) for table in tables) + len(sep)
    tables_per_row = (term_width - len(tab)) // table_width
    if tables_per_row == 0:
        tables_per_row = 1
    result = ''
    # Обрабатываем каждую строку максимального количества строк среди таблиц
    for row_index in range(max_rows):
        # Разделяем вывод на строки по tables_per_row таблиц в каждой
        for start in range(0, len(tables), tables_per_row):
            end = min(start + tables_per_row, len(tables))
            line_parts = []
            for i in range(start, end):
                # Добавляем строки таблицы, если строка существует
                if row_index < len(tables[i]):
                    line_parts.append(tables[i][row_index])
                else:
                    # Добавляем пустое место, если строк в таблице меньше
                    line_parts.append(' ' * len(tables[i][0]))
            result += tab + sep.join(line_parts).rstrip() + '\n'
    return result
def render_header(sep, width):
    header = '\n'
    header += sep + c.center(c.z('[x]COMBINATION DENSITY[c]'), width)
    return header
def render_sepline(sep, width):
    return sep + c.z(f"[x]{'.'*width}[c]") + '\n'
