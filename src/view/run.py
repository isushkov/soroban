import time
import re
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
        self.sep = '[x]'+self.v
        self.wsep = c.ln(self.sep)
        self.t_empty = '[x]__:__.__'
        self.mode = None # init_params
        self.t_goal = None # init_params
        self.t_usr = None # upd_acc
        self.t_oth = None # upd_acc
        self.t_spent = None # upd_stage
        # top.head
        self.head_start = ''
        self.head_status = '[x]Status: [y]TRAINING'
        self.head_timing = None # upd_top
        self.head_t_goal = '[x]t.Goal'
        self.head_t_spent = '[x]t.Now'
        self.head_t_usr = None # init_params (uname)
        self.head_t_oth = '[x]t.Oth'
        # top.acc
        self.acc_start = '[x]─ Stage ─'
        self.acc_operations = '[x]Operations'
        self.acc_result = '[x]Result'
        self.acc_timing = None # upd_top
        self.acc_t_goal = None # upd_top (ft_goal)
        self.acc_t_spent = '[x]00:00:00'
        self.acc_t_usr = None # upd_top (ft_usr)
        self.acc_t_oth = None # upd_top (ft_oth)
        # stage
        self.stage_start = '[x]Stage-1'
        self.stage_operations = ''
        self.stage_operation = None # upd_stage_operation
        self.stage_result = ''
        self.stage_timing = None # upd_stage_timing
        self.stage_t_goal = None # upd_stage_timing
        self.stage_t_spent = None # upd_stage_timing
        self.stage_t_usr = None # upd_stage_timing
        self.stage_t_oth = None # upd_stage_timing
        # w
        self.w_start = c.ln(self.acc_start)
        self.w_operations = None # init_ws
        self.w_operation = None # init_ws
        self.w_result = None # init_ws
        self.w_timing = None # init_ws
        self.wt = c.ln(self.t_empty)
        # cache
        self.stage = None
        self.donestages = ''
        self.donestages_count = 0
    # init
    def init_params(self, mode, goal, uname, sequence, ops_per_stage, pls_show):
        operations = sequence.split()
        start_number = operations.pop(0)
        total = s.safe_eval(sequence)
        # common
        self.uname = uname
        self.mode = mode
        self.t_goal = goal
        self.head_t_usr = '[x]t.'+uname
        # stage-start/delta-time
        self.operations_count = len(operations)
        self.ops_per_stage = ops_per_stage
        self.stages_total = self.operations_count // self.ops_per_stage + (1 if self.operations_count % self.ops_per_stage else 0)
        # calc width
        # если среди операндов если только плюсы
        existed_operands = list(set(s.split_operation(op)[0] for op in operations))
        if len(existed_operands) == 1 and existed_operands[0] == '+':
            if pls_show: space_for_operand = 1
            else:        space_for_operand = 0
        else:
            space_for_operand = 1
        self.w_operation = len(max(operations, key=len)) + space_for_operand
        self.w_result = max(c.ln(self.acc_result)+2, len(s.tostr(s.maxsum(start_number, operations))))
        self.w_timing = (self.wt + self.wsep) * (4 if self.t_goal else 3)
        self.w_operations = (self.w -
                             self.wsep - self.w_start -
                             self.wsep - self.w_result -
                             self.wsep - self.w_timing - self.wsep)
    # dynamic
    def upd_input(self, is_last_stage):
        self.input = f"[y]Your {'answer' if is_last_stage else 'stage-res'} is: "
    def upd_yesno(self, is_last_stage):
        self.yesno = dedent(f"""
            [y]<Space/Enter>  [c]{'FINISH' if is_last_stage else 'Continue'}
            [y]<a-Z>          [c]Restart the stage
            [y]<Esc>          [c]Exit
        """).strip()
    # top
    def upd_top(self, timing):
        is_passed = True if self.calls_top == 0 else False
        self.upd_head(is_passed)
        self.upd_acc(is_passed, timing)
        self.top = '\n'+'\n'.join([self.head, self.acc])
        # cache
        self.calls_top += 1
    def upd_head(self, is_passed):
        row = []
        status = '[x]Status:'
        if is_passed: status += f"[{'r' if self.mode == 'exam' else 'g'}]{self.mode.upper()}"
        else:         status += 'REPETITION'
        row.append([status, 'left', self.w_operations])
        row.append(['', 'left', self.w_result, ''])
        row.append([self.head_t_spent, 'center', self.wt])
        if self.t_goal:
            row.append([self.head_t_goal, 'center', self.wt])
        edges = '' if len(self.uname) > 4 else ' '
        row.append([self.head_t_usr, 'center', self.wt, edges])
        row.append([self.head_t_oth, 'center', self.wt])
        start = ' '*(self.wsep + self.w_start)
        self.head = start + self.table_th(row)
    def upd_acc(self, is_passed, timing):
        row = []
        row.append([self.acc_operations, 'left', self.w_operations])
        row.append([self.acc_result, 'center', self.w_result])
        k,color = ('passed','y') if is_passed else ('repeat','x')
        row.append([self.acc_t_spent, 'center', self.wt, ''])
        if self.t_goal:
            row.append([self.dec_t2ft(self.t_goal, v_color=color), 'center', self.wt, ''])
        row.append([self.dec_t2ft(timing[k]['usr'], v_color='c'), 'center', self.wt, ''])
        row.append([self.dec_t2ft(timing[k]['oth'], v_color='c'), 'center', self.wt, ''])
        self.acc = self.tl + self.acc_start + self.table_l(row)
    # stage
    def upd_stage_start(self, stage_number, user_errors):
        user_errors += 1
        user_errors = '' if user_errors == 1 else f"[r]x{user_errors if user_errors < 10 else '9'}"
        self.stage_start = self.sep + c.center(f'[x]{stage_number}/{self.stages_total}{user_errors}', self.w_start) + self.sep
        # cache
        self.stage = self.stage_start
        self.stage_operations = ''
    def upd_stage_ready(self, start_number):
        self.stage_ready = f'[x] Start-with: [c]{start_number} [y]<Any-key>[x] to start..'
        # cache
        self.calls_stage_ready += 1
    def upd_stage_operation(self, operand, pls_show, number):
        operand = '' if (operand == '+' and not pls_show) else operand
        self.stage_operation = c.rjust(f'[c]{operand}{number}', self.w_operation)
        # cache
        self.stage += self.stage_operation
        self.stage_operations += self.stage_operation
    # stage result: yes-no - before answer
    def upd_stage_result(self, total):
        self.stage_operations_pfx = ' '*(self.w_operations - c.ln(self.stage_operations)) + self.sep
        self.disp_stage_operations_pfx(end='', flush=True) # justify operations
        self.stage_result = '[c]'+c.center(s.tostr(total), self.w_result) + self.sep
        # cache
        self.stage += self.stage_operations_pfx
    # stage result: yes-no - after correct answer
    def upd_stage_result_ok(self, total):
        self.stage_result_ok = '[g]' + self.stage_result
        # cache
        self.stage += self.stage_result_ok
    def upd_stage_timing(self, t_spent, timing, is_passed, is_last_stage):
        self.donestages_count += 1 # for delta time
        row = []
        row.append([self.dec_t2ft(t_spent, v_color='c'), 'center', self.wt])
        if self.t_goal:
            if is_passed:
                stage_t_goal = self.dec_t2dt(t_spent, self.t_goal, is_last_stage)
            else:
                stage_t_goal = ' '*self.wt
            row.append([stage_t_goal, 'right', self.wt])
        k = 'passed' if is_passed else 'repeat'
        # pprint(timing)
        row.append([self.dec_t2dt(t_spent, float(timing[k]['usr']), is_last_stage), 'right', self.wt])
        row.append([self.dec_t2dt(t_spent, float(timing[k]['oth']), is_last_stage), 'right', self.wt])
        self.stage_timing = self.table_l(row, edges='')[len(self.sep):] # remove first sep for result
        # cache
        self.stage += self.stage_timing
        self.donestages = '\n'.join([self.donestages, self.stage]).strip()
    def dec_t2ft(self, seconds_total, v_color='c', z_color='x', colorize=True):
        if not seconds_total:
            return '[x]' + self.t_empty
        abs_seconds = abs(float(seconds_total))
        max_seconds = 99 * 60 + 99.99
        if abs_seconds >= max_seconds:
            return '99:59.99'
        minutes = int(abs_seconds // 60)
        seconds = round(abs_seconds % 60, 2)
        if minutes >= 99:
            minutes = 99
            seconds = min(seconds, 59.99)
        ft = f'{minutes:02d}:{seconds:05.2f}'
        # colorize
        if not colorize:
            return ft
        v_color, z_color = '['+v_color+']', '['+z_color+']'
        match = re.search('[1-9]\d*', ft)
        if match:
            zeros = ft[:match.start()]
            values = ft[match.start():]
            ft = z_color + zeros + v_color + values
        else:
            ft = v_color + ft
        return ft
    def dec_t2dt(self, spent, target, is_last_stage):
        if not target:
            return ' ' * self.wt
        delta = self.calc_delta(spent, target, is_last_stage)
        sign = '+' if delta >= 0 else '-'
        abs_delta = abs(delta)
        if abs_delta < 60:
            render = f'{sign}{abs_delta:.2f}'
        else:
            minutes = int(abs_delta // 60)
            seconds = abs_delta % 60
            render = f'{sign}{minutes}:{seconds:.2f}'
        return  ('[g]' if delta >= 0 else '[r]') + render
    def calc_delta(self, spent, target, is_last_stage):
        if is_last_stage:
            return target - spent
        done_ops = self.donestages_count * self.ops_per_stage
        time4stage = round((target / self.operations_count) * done_ops, 2)
        delta = time4stage - spent
        return delta

    # finish
    def upd_bottom(self):
        row = [self.w_start, self.w_operations, self.w_result] + ([self.wt] * (4 if self.t_goal else 3))
        self.bottom = self.table_b(row)
    def upd_finish(self, is_passed, end_time):
        if self.mode == 'exam':
            msg = '[g]Exam was passed!' if is_passed else '[r]The exam was not passed.'
        else:
            msg = '[g]Exercise was finished!'
        self.finish = self.padding(f"{msg}[x] Your time is: {self.dec_t2ft(end_time, v_color='g')}", [3,1,0,1])
    # leaderboard
    def upd_leaderboard(self, df, user_data):
        df_exam = df.loc[(df['is_exam'] == 1)]
        df_training = df.loc[(df['is_exam'] == 0) & (df['is_passed'] == 1)]
        df_repetitions = df.loc[(df['is_exam'] == 0) & (df['is_passed'] == 0)]
        table_exam = self.get_leaderboard_table(df_exam, '[g]', user_data)
        table_training = self.get_leaderboard_table(df_training, '[b]', user_data)
        table_repetitions = self.get_leaderboard_table(df_repetitions, '[x]', user_data)
        leaderboard_list = self.merge_tables(table_exam, table_training, table_repetitions)
        self.leaderboard = self.padding('\n'.join(leaderboard_list),[3,0,0,0])
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