# src/view
from src.view._view import View

class ViewAnalyze(View):
    def __init__(self):
        super().__init__()
        self.header = None
        self.fract = None
        self.integ = None
        self.total = None
        self.sepline = None
        tab, sep = ' '*3, ' '*3
        width_tables = len(c.remove_colors(r_integ.splitlines()[0])) - len(sep)

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

    def render_yn(value):
        return 'Yes' if value else 'No'
    def render_range_results(range_results, spoilers):
        min_result, max_result = range_results
        if not spoilers:
            min_result, max_result = blur(min_result), blur(max_result)
        return c.z(f'{min_result}-{max_result}')
    def blur(number):
        return re.sub(r'\d', 'x', str(number))
    def get_range_results(total, range_results=(0,0)):
        min_result, max_result = range_results
        if total < min_result: min_result = total
        if total > max_result: max_result = total
        return (min_result, max_result)
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

    # title
    if is_fract:
        title = f'0.1^{digit+1}'
    else:
        title = f'10 ^{digit}')
        shift2title = ['Units', 'Tens', 'Hundreds']

    def get_count_str(count):
        if count == 0: return c.z('[c] ')
        if count == 1: return c.z('[b]x')
        if count <= 3: return c.z(f'[g]{count}')
        if count <= 5: return c.z(f'[y]{count}')
        if count <= 9: return c.z(f'[r]{count}')
        if count > 9: return c.z('[r]*')
        return str(count)

    # c.z(f''),
    # c.z(f''),
    # c.z(f'[x]Start number:     [c]{start_number}'),
    # c.z(f'[x]Count operations: [c]{count_numbers}'),
    # c.z(f'[x]Existed operands: [c]{existed_operands}'),
    # c.z(f'[x]Decimal exist:    [c]{decimal_exist}'),
    # c.z(f'[x]Negative results: [c]{negative_results}'),
    # c.z(f'[x]Range numbers:    [c]{range_numbers}'),
    # c.z(f'[x]Range results:    [c]{range_results}'),
    # c.z(f'[x]Total provided:   [c]{total_provided}'),
    # c.z(f'[x]Total valid:      [c]{total_valid}'),
    # c.z(f'[x]Total correct:    [c]{total_correct}'),
    # c.z(f'')
    def upd_info(self, data):
        self.info = '\n\n'
        for k,v in data.items():
            self.info
        self.info += '\n'
