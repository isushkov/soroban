# src/view
from src.view._view import View

class ViewAnalyze(View):
    def __init__(self):
        super().__init__()
        self.decim = None
        self.integ = None
        self.total = None
        self.info = None
        self.totalinfo = None
        self.header = None
        self.sepline = None

    # TODO: check decimals
    # upds
    def upd_decim(self, data):
        raise Exception(c.z('[y]todo'))
    def upd_integ(self, data):
        raise Exception(c.z('[y]todo'))
    def upd_total(self, data):
        raise Exception(c.z('[y]todo'))
    def upd_info(self, data, spoilers):
        raise Exception(c.z('[y]todo'))
    def dec_dict(self, dictionary):
        # TODO: add decorators for values
        keys = '\n'.join(f"{key}:" for key in dictionary.keys())
        values = '\n'.join(dictionary.values())
        # TODO: merge_columns - add colors 'xgc'
        # TODO: merge_columns - check len with colors
        self.merge_columns(keys, values, colors='x')
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
    def upd_totalinfo(self, data):
        raise Exception(c.z('[y]todo'))
    def upd_header(self):
        self.upd_title('[x]COMBINATION DENSITY', char=' ')
    def upd_sepline(self, sep='.', color='x'):
        self.sepline = f'[{color}]'+'.'*self.w+'[c]'

    # decs
    def dec_density_table(self, title, data_left, data_right):
        raise Exception(c.z('[y]todo'))
    def dec_merge_tables(self, left_table, right_table):
        raise Exception(c.z('[y]todo'))

    # def get_table(digit, density_pos, density_neg, is_decim=False):
    # # # title
    # # if is_decim:
    # #     title = f'0.1^{digit+1}'
    # # else:
    # #     title = f'10 ^{digit}'
    # #     shift2title = ['Units', 'Tens', 'Hundreds']
    #     table = []
    #     # title
    #     if digit == 'total':
    #         title = '──[ TOTAL ]──'
    #     else:
    #         if is_decim:
    #             title = f'──[ 0.1^{digit+1} ]──'
    #         else:
    #             shift2title = {0:'──[ Units ]──', 1:'──[ Tens ]───', 2:'[ Hundreds ]─'}
    #             title = shift2title.get(digit, f'──[ 10 ^{digit} ]──')
    #     table.append(c.z(f'[x]   ┌───{title}───┐     '))
    #     table.append(c.z( '[x]┌───┴─[ - ]─┬───┬─[ + ]─┴───┐'))
    #     # rows
    #     for y in range(9, -1, -1):
    #         row_middle = f' │ {y} │ '
    #         row_left   = get_density_row(y, density_neg, range(9, 0, -1))
    #         row_right  = get_density_row(y, density_pos, range(1, 10))
    #         table.append(c.z(f"[x]│ [c]{row_left}[x]{row_middle}[c]{row_right}[x] │"))
    #     # footer
    #     table.append(c.z('[x]├───────────┼───┼───────────┤'))
    #     table.append(c.z('[x]└─987654321─┘   └─123456789─┘'))
    #     return table
    # def render_tables(sep, tables, term_width, tab=' '*3):
    #     if not tables:
    #         return ''
    #     # Определяем максимальное количество строк среди всех таблиц
    #     max_rows = max(len(table) for table in tables)
    #     # Ширина одной таблицы с учетом сепаратора
    #     table_width = max(len(c.remove_colors(table[0])) for table in tables) + len(sep)
    #     tables_per_row = (term_width - len(tab)) // table_width
    #     if tables_per_row == 0:
    #         tables_per_row = 1
    #     result = ''
    #     # Обрабатываем каждую строку максимального количества строк среди таблиц
    #     for row_index in range(max_rows):
    #         # Разделяем вывод на строки по tables_per_row таблиц в каждой
    #         for start in range(0, len(tables), tables_per_row):
    #             end = min(start + tables_per_row, len(tables))
    #             line_parts = []
    #             for i in range(start, end):
    #                 # Добавляем строки таблицы, если строка существует
    #                 if row_index < len(tables[i]):
    #                     line_parts.append(tables[i][row_index])
    #                 else:
    #                     # Добавляем пустое место, если строк в таблице меньше
    #                     line_parts.append(' ' * len(tables[i][0]))
    #             result += tab + sep.join(line_parts).rstrip() + '\n'
    #     return result

    def dec_yn(self, value):
        return 'Yes' if value else 'No'
    def dec_blur_numbers(self, number):
        return re.sub(r'\d', 'x', str(number))
    def dec_range(self, range_results, spoilers):
        min_result, max_result = range_results
        if not spoilers:
            min_result = self.dec_blur_numbers(min_result)
            max_result = self.dec_blur_numbers(max_result)
        return f'{min_result}-{max_result}'
    def dec_counter(count, one_digit_format=True):
        if count == 0: return '[c] '
        if count == 1: return '[b]x'
        if count <= 3: return f'[g]{count}'
        if count <= 5: return f'[y]{count}'
        if count <= 9: return f'[r]{count}'
        if count > 9:
            if one_digit_format:
                return '[r]*'
            return f'[r]{count}'
        raise Exception(c.z(f'[r]ERROR: dec_count():[c] unknown value {count}'))
