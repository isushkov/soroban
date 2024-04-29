from functools import reduce
import time
# src
import src.sequence as s
# src/view
from src.view._view import View
# src/helpers
import src.helpers.colors as c

class ViewRun(View):
    def __init__(self):
        self.delta_empty = '--:--:--'
        self.len_dt = len(self.df_empty)
        self.row = {
            'start': None,
            'operations': None,
            'result': None,
            'deltas': None
        }

    # Stage99 x99: (operation, operation, ...) <-> result deltas
    def set_row_lens(self, operations):
        self.len_start = len('Stage99 x2:')
        self.len_operation = len(max(operations, key=len)) + 1
        # TODO: количество операций в stage * len_operation
        self.len_operations =
        self.len_result = len(s.tostr(reduce(s.get_resNmaxres, operations, (operations[0],0))[1]))
        self.len_delta = len(self.delta_empty)
        если study тогда 3 иначе 2
        self.len_deltas =

    # view
    def ready(self, mode, start_number):
        color = '[r]' if mode == 'exam' else '[g]'
        c.p(f'{color}{mode.upper()}. [y]Get ready.[x] Start number:[c] {start_number}')
    def header(self, cfg, mode, goal):
        start_stage = ' '.ljust(self.start_stage_max_len)
        operations = 'Operations'.ljust(cfg.numbers_per_stage * self.operation_max_len)
        result = 'Result'.ljust(self.result_max_len)
        dt_target = 'Δt.goal'.center(self.len_dt)
        dt_user   = 'Δt.user'.center(self.len_dt)
        dt_other  = 'Δt.other'.center(self.len_dt)
        dts = [dt_target] + [dt_user, dt_other] if goal else [dt_user, dt_other]
        c.p(f'[x]{self.tab}{self.sep.join([start_stage, operations, result] + dts)}{self.tab}')
    def start_stage(self, stage_number, user_errors):
        user_errors = f' [r]x{min(user_errors+1, 9)}' if user_errors else ''
        view = c.ljust(c.z(f'[x]Stage-{min(int(stage_number), 99)}{user_errors}:'), self.start_stage_max_len)
        print(self.tab + view, end='', flush=True)
    def operation(self, operand, number, cfg):
        operand = '' if (operand == '+' and not cfg.show_plus) else operand
        view = f' {operand}{number}'.rjust(self.operation_max_len)
        print(view, end='', flush=True)
    def show_result(self, result):
        print(f' ={result}')
    def ask_yesno(self, is_last_stage):
        menu  = f"   [y]<Space/Enter>[c]   {'FINISH' if is_last_stage else 'Continue'}\n"
        menu +=  "   [y]<a-Z>[c]           Restart the stage\n"
        menu +=  "   [y]<Esc>[c]           Exit"
        c.p(menu)
    def ask_input(self):
        msg = 'answer' if is_last_stage else 'stage-result'
        print(c.z(f'[y]Your {msg} is: '), end='', flush=True)
    # deltas
    def deltas(self, is_passed, timing, start_time):
        spend_time = round(time.time(), 2) - start_time
        # только если это study
        if timing['goal']:
            self.delta(float(timing['goal']) - spend_time)
        # best_user, best_other
        k = 'passed' if is_passed else 'repeat'
        for i in ['usr', 'oth']:
            self.delta((float(timing[k][i]) - spend_time) if timing[k].get(i) else False)
        print(self.tab)
    def delta(self, time):
        view = c.z(f"[{'r' if time < 0 else 'g'}]{self.f_time(time, unary_plus=True)}") if time else c.z(f'[x]{self.df_empty}')
        print(self.sep.join(view), end='', flush=True)
    def f_time(self, seconds_total, unary_plus):
        unary_plus = '+' if unary_plus else ''
        sign = '-' if seconds_total < 0 else unary_plus
        seconds_total = abs(seconds_total)
        max_seconds = 99 * 60 + 99.99
        if seconds_total >= max_seconds:
            return sign + '99:59.99'
        minutes = int(seconds_total // 60)
        seconds = round(seconds_total % 60, 2)
        if minutes >= 99:
            minutes = 99
            seconds = min(seconds, 59.99)
        formatted_time = f'{sign}{minutes:02d}:{seconds:05.2f}'
        return formatted_time
    # finish
    def finish(self, mode, is_passed, end_time):
        if mode == 'exam':
            msg = '[g]Exam was passed!' if is_passed else '[r]The exam was not passed.'
        else:
            msg = '[g]Exercise was finished!'
        c.p(f'{msg}[c] Your time is: [y]{self.f_time(end_time, unary_plus=False)}')
    def leaderboard(self, df, user_data):
        df_exam = df.loc[(df['is_exam'] == 1)]
        df_training = df.loc[(df['is_exam'] == 0) & (df['is_passed'] == 1)]
        df_repetitions = df.loc[(df['is_exam'] == 0) & (df['is_passed'] == 0)]
        table_exam = self.get_leaderboard_table(df_exam, '[g]', user_data)
        table_training = self.get_leaderboard_table(df_training, '[b]', user_data)
        table_repetitions = self.get_leaderboard_table(df_repetitions, '[x]', user_data)
        table = self.merge_tables(table_exam, table_training, table_repetitions)
        print('')
        for line in table:
            print('   '+line)
        print('')
    def get_leaderboard_table(self, df, row_color, user_data):
        if user_data:
            user_id = user_data['id']
            user_rank = user_data['rank']
        table = []
        table_size=9
        if df.empty:
            table.append(c.z('[x]│ None                        │'))
            table.append(c.z('[x]└─────────────────────────────┘'))
            return table
        # find user in df
        is_user_here = user_id and not df[df.index == user_id].empty
        # first_9
        is_user_found = False
        for i, row in df.head(table_size).iterrows():
            if is_user_here and i == user_id:
                is_user_found = True
                table.append(self.row2rec(row, row_color, user_data))
                continue
            table.append(self.row2rec(row, row_color, user_data=False))
        # if records is more than table_size
        empty_record = c.z('[x]│ .. ...         ... ........ │')
        rows_count = df.shape[0]
        if rows_count > table_size:
            table.append(empty_record)
        # if user rank worse than 9
        if is_user_here and not is_user_found:
            table.append(self.row2rec(row, row_color, user_data))
            # if there records with rank worse than user rank
            if rows_count > user_rank:
                table.append(empty_record)
        table.append(c.z('[x]└─────────────────────────────┘'))
        return table
    def row2rec(self, row, row_color, user_data=False):
        rank, name, time, date = (
            (user_data['rank'], user_data['user_name'], user_data['time'], user_data['date'])
            if user_data else
            (row['rank'], row['user_name'], row['time'], row['date'])
        )
        rank = '99' if rank > 99 else (f'{rank} ' if rank < 10 else str(rank))
        name = name.ljust(6) if len(name) < 6 else name
        color = '[y]' if user_data else row_color
        return c.z(f'[x]│ {color}{rank} {name} {time}[x] {date} │')
    def merge_tables(self, exam, training, repetitions):
        table = []
        table.append(c.z('[x]  ┌─ Leaderboard ─────────────────────────────────────────────────────────────────────┐'))
        table.append(c.z('[x]  │                             ┌────────────────────── Training ─────────────────────┴─┐'))
        table.append(c.z('[x]┌─── [g]EXAM PASSED[x] ─────────────┐─┴─ [b]Passed[x] ──────────────────┐─── With repetitions ──────┴─┐'))
        max_length = max(len(exam), len(training), len(repetitions))
        sep = ' '*30
        for i in range(max_length):
            exm = exam[i] if i < len(exam) else sep
            trg = training[i] if i < len(training) else sep
            rep = repetitions[i] if i < len(repetitions) else sep
            # eettrr  eettrr
            #   ttrr  eett
            #     rr  ee
            if exm.strip() and trg.strip():
                trg = self.cut_line(trg)
            if trg.strip() and rep.strip():
                rep = self.cut_line(rep)
            # eettrr
            # ee  rr
            #     rr
            # if not trg.strip() and rep.strip():
            #     trg = trg[1:]
            new_line = exm + trg + rep
            table.append(new_line)
        return table
    def cut_line(self, line):
        return c.z('[x]'+line[6:])
