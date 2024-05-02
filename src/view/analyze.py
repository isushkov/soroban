import re
from pprint import pprint
from textwrap import dedent
# src
import src.sequence as s
# src/view
from src.view._view import View
import src.helpers.colors as c

class ViewAnalyze(View):
    def __init__(self):
        super().__init__()
    # tables
    def upd_decim(self, data_digits):
        self.decim = self.dec_row_tables(data_digits)
    def upd_integ(self, data_digits):
        self.integ = self.dec_row_tables(data_digits)
    def upd_total(self, data_total):
        self.total = self.dec_digit_table(data_total, title='TOTAL')
    def dec_row_tables(self, data_digits):
        padding, lensep, w_table = [3,0,0,0], 2, 29
        tables = [self.dec_digit_table(data, digit) for digit,data in data_digits.items()]
        rows = self.chunk_list(tables, (self.w - 2*padding[0]) // (w_table+lensep))
        render = ''
        render, i, len_rows = '', 1, len(rows)
        for row in rows:
            render += self.padding(self.merge(*row, sep=' '*lensep), padding)
            if i != len_rows: render += '\n'
            i += 1
        return render.strip('\n') or ''
    def chunk_list(self, lst, chunk_size):
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
    def dec_digit_table(self, data, title):
        # header
        if not isinstance(title, str):
            title = title - self.max_f
            title = {0:'Units', 1:'Tens', 2:'Hundrds'}.get(title) or f'10^{title+1}'
        title = f' {title} '
        table = f'[x]    ┌─────{title.center(9,"─")}─────┐    \n'
        table += '[x]┌───┴─[ - ]─┬───┬─[ + ]─┴───┐\n'
        for y in range(9, -1, -1):
            row_right = self.dec_density_row(data[y]['pos'])
            row_left  = self.dec_density_row(data[y]['neg'])
            table += f"[x]│ [c]{row_left}[x] │ {y} │ [c]{row_right}[x] │\n"
        # footer
        table += '[x]├───────────┼───┼───────────┤\n'
        table += '[x]└─987654321─┘   └─123456789─┘'
        return table
    def dec_density_row(self, row):
        return ''.join(self.dec_counter(char) for char in row)
    def dec_counter(self, count):
        count = 10 if count == 'm' else int(count)
        if count == 0: return '[c] '
        if count == 1: return '[b]x'
        if count <= 3: return f'[g]{count}'
        if count <= 5: return f'[y]{count}'
        if count <= 9: return f'[r]{count}'
        if count >= 10: return '[r]*'
        raise Exception(c.z(f'[r]ERROR: dec_count():[c] unknown value {count}'))

    # info
    def upd_info(self, data, spoilers):
        (start_number, ops_count, ops_operands, dec_exist, neg_exist, range_numbers,
         range_results, total_provided, total_correct, total_calculated) = data.values()
        # decorate
        ops_operands = ''.join(ops_operands)
        dec_exist = self.dec_yn(dec_exist)
        neg_exist = self.dec_yn(neg_exist)
        if not spoilers:
            range_numbers = self.dec_blur_digits(range_numbers)
            range_results = self.dec_blur_digits(range_results)
        # provided
        color = '[g]' if total_provided else '[r]'
        if not spoilers:
            total_provided = self.dec_yn(total_provided)
        total_provided = color + total_provided
        # calculated
        color = '[g]' if total_correct else '[r]'
        if not spoilers: total_summary = f'Total correct:    {color}{self.dec_yn(total_correct)}'
        else:            total_summary = f'Total calculated: {color}{total_calculated}'
        # apply
        self.info = dedent(f"""
            [x]Start number:     [c]{start_number}
            [x]Count operations: [c]{ops_count}
            [x]Existed operands: [c]{ops_operands}
            [x]Decimal exist:    [c]{dec_exist}
            [x]Negative exist:   [c]{neg_exist}
            [x]Range numbers:    [c]{range_numbers}
            [x]Range results:    [c]{range_results}
            [x]Total provided:   [c]{total_provided}
            [x]{total_summary}
        """).strip()
    def dec_yn(self, value, colors=False, reverse=False):
        msg = 'Yes' if value else 'No'
        if not reverse:
            c = ('[g]' if value else '[r]') if value else ''
        else:
            c = '' if colors else ('[g]' if value else '[r]')
        return c+msg
    def dec_blur_digits(self, number):
        return re.sub(r'\d', 'x', str(number))
    def dec_range(self, range_results, spoilers):
        min_result, max_result = range_results
        if not spoilers:
            min_result = self.dec_blur_digits(min_result)
            max_result = self.dec_blur_digits(max_result)
        return f'{min_result}-{max_result}'

    # header/totalinfo
    def upd_header(self):
        w_tables = max(map(lambda s: s.find('\n'), [self.decim, self.integ, self.total]))
        self.header = self.padding(c.center('[x]COMBINATION DENSITY', w_tables), [3,1,0,0])
    def upd_totalinfo(self):
        self.totalinfo = self.padding(
            self.merge(self.total, '\n\n'+self.info, sep=' '*2),
            [3,0,0,1]
        )
