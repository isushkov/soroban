import time
from textwrap import dedent
from pprint import pprint
# src
import src.sequence as s
# src/view
from src.view._view import View
# src/helpers
import src.helpers.colors as c

class ViewRun(View):
    def __init__(self, w_user):
        super().__init__(w_user)
        # common
        # t     : time sec
        # ft    : 00:00:00
        # loc_ft: 00:00:00 +color +justify
        # dt    : +0:00:00
        # loc_dt: +0:00:00 +color +justify
        # self.sep = '[x]|'
        self.tab = '[b]│'
        self.sep = '[x]│'
        self.wtab = c.ln(self.tab)
        self.wsep = c.ln(self.sep)
        self.ft_empty = '[x]--:--.--'
        self.dt_empty = '[x] -:--.--'
        self.mode = None # init_params
        self.t_goal = None # init_params
        self.t_usr = None # upd_acc
        self.t_oth = None # upd_acc
        self.t_now = None # upd_stage
        # top.head
        self.head_start = ''
        self.head_status = '[x]Status: [g]PASSING'
        self.head_timing = None # upd_top
        self.head_t_goal = '[x]t.Goal'
        self.head_t_now = '[x]t.Now'
        self.head_t_usr = None # init_params (uname)
        self.head_t_oth = '[x]t.Others'
        # top.acc
        self.acc_start = ''
        self.acc_operations = '[x]Operations'
        self.acc_result = '[x]Result'
        self.acc_timing = None # upd_top
        self.acc_t_goal = None # upd_top (ft_goal)
        self.acc_t_now = '[c]00:00:00'
        self.acc_t_usr = None # upd_top (ft_usr)
        self.acc_t_oth = None # upd_top (ft_oth)
        # stage
        self.stage_start = '[x]Stage-1'
        self.stage_operations = ''
        self.stage_operation = None # upd_stage_operation
        self.stage_result = ''
        self.stage_timing = None # upd_stage_timing
        self.stage_t_goal = None # upd_stage_timing
        self.stage_t_now = None # upd_stage_timing
        self.stage_t_usr = None # upd_stage_timing
        self.stage_t_oth = None # upd_stage_timing
        # w
        self.w_start = len('Stage-9x2')
        self.w_operations = None # init_ws
        self.w_operation = None # init_ws
        self.w_result = None # init_ws
        self.w_timing = None # init_ws
        self.wt = len('__:__.__')
    # init
    def init_params(self, mode, goal, uname):
        self.mode = mode
        self.t_goal = s.tonum(goal)*60
        self.head_t_usr = '[x]t.'+uname
    def init_ws(self, sequence, num_per_stage, pls_show):
        operations = sequence.split()
        start_number = operations.pop(0)
        total = s.safe_eval(sequence)
        self.w_operation = len(max(operations, key=len)) + (1 if pls_show else 0)
        # w_result: либо title / либо сумма
        self.w_result = max(len(self.acc_result), len(s.tostr(s.maxsum(start_number, operations))))
        self.w_timing = (self.wt + self.wsep) * (4 if self.t_goal else 3) + self.wtab
        self.w_operations = (self.w
                             - self.wtab - self.w_start - self.wsep
                             - self.w_result - self.wsep
                             - self.w_timing)
        # print(self.w_start*'s')
        # print(self.w_operations*'o')
        # print(self.w_result*'r')
        # print(self.w_timing*'t')

    # dynamic
    def upd_ready(self, start_number):
        color = '[r]' if self.mode == 'exam' else '[g]'
        self.ready = c.z(f'{color}{self.mode.upper()}. [y]Get ready.[x] Start number:[c] {start_number}')
    def upd_input(self, is_last_stage):
        self.input = f"[y]Your {'answer' if is_last_stage else 'stage-res'} is: "
    def upd_yesno(self, is_last_stage):
        self.yesno = dedent(f"""
            [y]<Space/Enter>  [c]{'FINISH' if is_last_stage else 'Continue'}
            [y]<a-Z>          [c]Restart the stage
            [y]<Esc>          [c]Exit
        """).strip()

    # top
    def upd_top(self, is_passed, timing):
        self.upd_head(is_passed)
        # 0: init acc-row
        # 1: switch acc-row to repetitions
        if self.calls_upd_acc <= 1:
            self.upd_acc(is_passed, timing)
            self.calls_upd_acc += 1
        self.top = self.join([self.head, self.acc], char='')
    def upd_head(self, is_passed):
        self.head_start = self.tab + c.ljust(self.head_start, self.w_start) + self.sep
        if not is_passed: self.head_status = '[x]Status: [r]REPETITION'
        self.head_status = c.ljust(self.head_status, self.w_operations + self.wsep + self.w_result) + self.sep
        self.head_timing = self.dec_top_timing(self.head_t_goal, self.head_t_now, self.head_t_usr, self.head_t_oth)
        # head
        self.head = self.join([self.head_start, self.head_status, self.head_timing], char='') + '\n'
    def upd_acc(self, is_passed, timing):
        self.acc_start = self.tab + c.ljust(self.acc_start, self.w_start) + self.sep
        self.acc_operations = c.ljust(self.acc_operations, self.w_operations) + self.sep
        self.acc_result = c.ljust(self.acc_result, self.w_result) + self.sep
        # timing.goal
        k,color = ('passed','[y]') if is_passed else ('repeat','[x]')
        self.acc_t_goal = (color + self.dec_t2ft(self.t_goal)) if self.t_goal else ''
        self.acc_t_now  = '[c]00:00:00'
        self.acc_t_usr  = '[x]'+ self.dec_t2ft(float(timing[k]['usr']))
        self.acc_t_oth  = '[x]'+ self.dec_t2ft(float(timing[k]['oth']))
        self.acc_timing = self.dec_top_timing(self.acc_t_goal, self.acc_t_now, self.acc_t_usr, self.acc_t_oth)
        # acc
        self.acc = self.join([self.acc_start, self.acc_operations, self.acc_result, self.acc_timing], char='')
    def dec_top_timing(self, goal, now, usr, oth):
        goal = c.center(goal, self.wt) + self.sep if goal else ''
        now, usr = map(lambda x: c.center(x, self.wt) + self.sep, [now, usr])
        oth = c.center(oth, self.wt) + self.tab
        return goal + now + usr + oth

    # stage
    def upd_stage_start(self, stage_number, user_errors):
        user_errors += 1
        user_errors = '' if user_errors == 1 else f" [r]x{user_errors if user_errors < 10 else '*'}"
        stage_number = min(stage_number, 9) if stage_number < 10 else 'X'
        self.stage_start = c.ljust(f'[x]Stage-{stage_number}{user_errors}', self.w_start) + self.sep
    def upd_stage_operation(self, operand, pls_show, number):
        operand = '' if (operand == '+' and not pls_show) else operand
        self.stage_operation = c.rjust(f'[c]{operand}{number}', self.w_operation)
        self.stage_operations += self.stage_operation
    def upd_stage_result(self, total, color):
        self.stage_operations_pfx = ' '*(self.w_operations - c.ln(self.stage_operations)) + self.sep
        self.disp_stage_operations_pfx(oneline=True) # justify operations
        self.stage_result = c.ljust(f'[{color}]={s.tostr(total)}', self.w_result) + self.sep
        return -len(self.stage_result)
    def upd_stage_result_ok(self, total, color):
        self.upd_stage_result(total, color)
        self.stage_result_ok = self.stage_result
    def upd_stage_timing(self, is_passed, timing, start_time, now):
        # goal - dt
        if self.t_goal:
            if is_passed:
                self.dt_goal = self.dec_t2dt(self.t_goal - self.t_now)
                self.stage_t_goal = c.ljust(self.dt_goal, self.wt) + self.sep
            else:
                self.stage_t_goal = c.ljust(self.dt_empty, self.wt) + self.sep
        else:
            self.stage_t_goal = ''
        # now - ft
        self.t_now = now - start_time
        self.ft_now = self.dec_t2ft(self.t_now) # ft, not dt
        self.stage_t_now = c.ljust('[c]'+self.ft_now, self.wt) # ft, not dt
        # usr/oth - dt
        k = 'g','passed' if is_passed else 'repeat'
        self.t_usr = float(timing[k]['usr'])
        self.t_oth = float(timing[k]['oth'])
        self.dt_usr = self.dec_t2dt(self.t_usr - self.t_now)
        self.dt_oth = self.dec_t2dt(self.t_oth - self.t_now)
        self.stage_t_usr = c.ljust(self.dt_usr, self.wt)
        self.stage_t_oth = c.ljust(self.dt_oth, self.wt)
        # render
        self.stage_timing = self.stage_t_goal + self.sep.join([
            self.stage_t_now, self.stage_t_usr, self.stage_t_oth,
        ])
    def dec_t2ft(self, seconds_total):
        seconds_total = abs(seconds_total)
        max_seconds = 99 * 60 + 99.99
        if seconds_total >= max_seconds:
            return '99:59.99'
        minutes = int(seconds_total // 60)
        seconds = round(seconds_total % 60, 2)
        if minutes >= 99:
            minutes = 99
            seconds = min(seconds, 59.99)
        formatted_time = f'{minutes:02d}:{seconds:05.2f}'
        return formatted_time
    def dec_t2dt(self, seconds_total, color=True):
        sign = '+' if seconds_total >= 0 else '-'
        abs_seconds = abs(seconds_total)
        if abs_seconds < 10:
            render = f'{sign}{abs_seconds:.2f}'
        elif abs_seconds < 60:
            render = f'{sign}{abs_seconds:.2f}'
        else:
            minutes = int(abs_seconds // 60)
            seconds = abs_seconds % 60
            render = f'{sign}{minutes}:{seconds:.2f}'
        color = ('[g]' if seconds_total < 0 else '[r]') if color else ''
        return  color + render

    # finish
    def upd_finish(self, is_passed, end_time):
        if self.mode == 'exam':
            msg = '[g]Exam was passed!' if is_passed else '[r]The exam was not passed.'
        else:
            msg = '[g]Exercise was finished!'
        self.finish = f'{msg}[c] Your time is: [y]{self.dec_t2ft(end_time, pls=False)}'
    # leaderboard
    def upd_leaderboard(self, df, user_data):
        df_exam = df.loc[(df['is_exam'] == 1)]
        df_training = df.loc[(df['is_exam'] == 0) & (df['is_passed'] == 1)]
        df_repetitions = df.loc[(df['is_exam'] == 0) & (df['is_passed'] == 0)]
        table_exam = self.get_leaderboard_table(df_exam, '[g]', user_data)
        table_training = self.get_leaderboard_table(df_training, '[b]', user_data)
        table_repetitions = self.get_leaderboard_table(df_repetitions, '[x]', user_data)
        leaderboard_list = self.merge_tables(table_exam, table_training, table_repetitions)
        self.leaderboard = '\n'.join(leaderboard_list)
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
            if exm.strip() and trg.strip():
                trg = self.cut_line(trg)
            if trg.strip() and rep.strip():
                rep = self.cut_line(rep)
            new_line = exm + trg + rep
            table.append(new_line)
        return table
    def cut_line(self, line):
        return c.z('[x]'+line[6:])
