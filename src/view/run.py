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
        self.acc_ops = '[x]Operations'
        self.acc_result = '[x]Result'
        self.acc_timing = None # upd_top
        self.acc_t_goal = None # upd_top (ft_goal)
        self.acc_t_spent = '[x]00:00:00'
        self.acc_t_usr = None # upd_top (ft_usr)
        self.acc_t_oth = None # upd_top (ft_oth)
        # stage
        self.stage_start = None
        self.stage_ops = ''
        self.stage_op = None # upd_stage_op
        self.stage_result = ''
        self.stage_timing = None # upd_stage_timing
        self.stage_t_goal = None # upd_stage_timing
        self.stage_t_spent = None # upd_stage_timing
        self.stage_t_usr = None # upd_stage_timing
        self.stage_t_oth = None # upd_stage_timing
        # cache
        self.stage = None
        self.donestages = ''
        self.n_donestages = 0
        self.uname_note = dedent('''
            [y]NOTE: [x]You can specify a temporary username using the optional argument [b]--user-name=[x]<user-name>
            [y]NOTE: [x]or set a permanent one in [b]config.yml [x](--user-name has a higher priority):
            [y]NOTE: [x]    [b].common.user_name:[c] <user-name> [x]# 1-6 chars
        ''').strip()
    # init
    def init_params(self, mode, goal, uname, sequence, n_ops_per_stage, pls_show):
        ops = sequence.split()
        start_number = ops.pop(0)
        # common
        self.uname = uname
        self.mode = mode
        self.t_goal = goal
        self.n_ops = len(ops)
        self.n_ops_per_stage = n_ops_per_stage
        self.n_ops_last_stage = self.n_ops % n_ops_per_stage
        self.n_stages = self.n_ops // n_ops_per_stage + (1 if self.n_ops_last_stage else 0)
        # start/result/timing/final
        self.w_start = max(c.ln(self.acc_start), c.ln(f'{self.n_stages}/{self.n_stages}x9')+2)
        self.w_result = max(c.ln(self.acc_result)+2, len(s.tostr(s.maxsum(s.tonum(start_number), ops)))+2)
        self.wt = c.ln(self.t_empty)
        self.w_timing = 0 if self.mode == 'exam' else ((self.wt+self.wsep)*(4 if self.t_goal else 3)) - self.wsep
        self.total = s.safe_eval(sequence)
        # hooks: зависит от оставшейся ширины экрана
        # если среди операндов только плюсы и его не показывать len op -1
        existed_operands = list(set(s.split_operation(op)[0] for op in ops))
        pls_shift = 1 if len(existed_operands) == 1 and existed_operands[0] == '+' and not pls_show else 0
        self.w_op = len(max(ops, key=len)) - pls_shift + 1 # for space
        if self.mode == 'exam':
            self.w_ops = self.w - self.wsep - self.wsep
        else:
            # w_ops: atleast status title lenght
            self._min_w_ops = len(' Status: REPETITION ')
            self._w_occupied = (self.wsep + self.w_start +
                                self.wsep +
                                self.wsep + self.w_result +
                                self.wsep + self.w_timing + self.wsep)
            self.w_ops = self.w - self._w_occupied
            if self.w_ops < self._min_w_ops:
                self.w_ops = self._min_w_ops
        self.n_rows_per_stage = self.calc_n_rows_per_stage(self.n_ops_per_stage)
        self.n_rows_last_stage = self.calc_n_rows_per_stage(self.n_ops_last_stage)
        self.w_status = self.w_ops + self.w_result
        # x_pos
        self.x_start  = 1 + self.wsep
        if self.mode == 'exam':
            self.x_ops = self.x_start
        else:
            self.x_ops = self.x_start + self.w_start + self.wsep
        # self.x_result = self.x_ops + self.w_ops + self.wsep
    def calc_n_rows_per_stage(self, n_stage_ops):
        n_ops_per_row = self.w_ops // self.w_op or 1
        n_stage_rows = n_stage_ops // n_ops_per_row + (1 if n_stage_ops % n_ops_per_row else 0)
        return n_stage_rows

    # menus
    def upd_ready(self, start_number):
        self.ready = '\n'+self.dec_menu(
            f'[x]Start-with: [c]{start_number} [y]<Any-key>[x] to start..'
        )
    def upd_yesno(self, is_last_stage):
        self.yesno = '\n'+self.dec_menu(dedent(f'''
            [y]<Space/Enter>  [c]{'FINISH' if is_last_stage else 'Continue'}
            [y]<a-Z>          [c]Restart the stage
            [y]<Esc>          [c]Exit
        '''))
    def menu_yesno(self):
        key = self.getch()
        if key in [' ', '\r', '\n']:
            return True
        elif key == '\x1b':
            c.p('[g]Exit.')
            exit(130)
        else:
            return False
    def upd_input(self, total, is_last_stage):
        msg = f"[x]Your [y]{'answer' if is_last_stage else 'stage result'} is: [c]"
        self.input = '\n'+self.dec_menu(msg)
        self.x_input = self.wsep + c.ln(msg) + 1 + 1 # + padding_left + space
    def menu_input(self):
        # prepare cursor
        self.cursor_shift(y=-2)
        self.cursor_move(x=self.x_input)
        # input
        self.echo()
        answer = input()
        self.noecho()
        self.clear_lines(1)
        return answer
    # cursors
    def clear_menu(self, menu):
        self.cursor_shift(y=999)
        self.cursor_shift(y=-len(menu.splitlines(keepends=True))+1)
        self.cursor_move(x=0)
        self.clear('down')
        self.render_footer()
    # menus.dec
    def dec_menu(self, msg):
        max_length = max(c.ln(line) for line in msg.split('\n'))
        padding_left = 1
        padding_right = self.calc_w4menu() - (padding_left + max_length + 2) # for border
        return self.border(self.padding(msg.strip(), [padding_left,0,padding_right,0])).strip()
    def calc_w4menu(self):
        min_w = 30
        if self.mode == 'exam': w = self.wsep + self.w_ops // 2 + self.wsep
        else: w = self.wsep + self.w_start + self.wsep + self.w_ops + self.wsep
        return w if w > min_w else min_w

    # top
    def upd_top(self, timing):
        self.top = '\n' # for top padding
        is_passed = True if self.calls_top == 0 else False
        self.upd_head(is_passed)
        if self.mode == 'exam':
            self.top += self.head
        else:
            self.upd_acc(is_passed, timing)
            self.top += '\n'.join([self.head, self.acc])
        # state
        self.calls_top += 1
    def upd_head(self, is_passed):
        row = []
        status = '[x]Status:'
        if self.mode == 'exam':
            status += '[r]'+self.mode.upper()
            if self.t_goal:
                t_goal = self.dec_t2ft(self.t_goal, v_color='y')
                status += self.tcolor+self.h + f' Goal:{t_goal} '
            # state
            self.head = self.table_th([[status, 'left', self.w_ops]])
        else:
            # status/result
            status += '[g]'+self.mode.upper() if is_passed else 'REPETITION'
            row.append([status, 'left', self.w_ops])
            row.append(['', 'left', self.w_result, ''])
            # timing
            row.append([self.head_t_spent, 'center', self.wt])
            if self.t_goal:
                row.append([self.head_t_goal, 'center', self.wt])
            uname = '[x]t.'+self.uname
            edges = '' if c.ln(uname) > 4 else ' '
            row.append([uname, 'center', self.wt, edges])
            row.append([self.head_t_oth, 'center', self.wt])
            # state
            self.head = ' '*(self.wsep + self.w_start) + self.table_th(row)
    def upd_acc(self, is_passed, timing):
        row = []
        # ops/result
        row.append([self.acc_ops, 'left', self.w_ops])
        row.append([self.acc_result, 'center', self.w_result])
        # timing
        k,color = ('passed','y') if is_passed else ('repeat','x')
        row.append([self.acc_t_spent, 'center', self.wt, ''])
        if self.t_goal:
            row.append([self.dec_t2ft(self.t_goal, v_color=color), 'center', self.wt, ''])
        row.append([self.dec_t2ft(timing[k]['usr'], v_color='c'), 'center', self.wt, ''])
        row.append([self.dec_t2ft(timing[k]['oth'], v_color='c'), 'center', self.wt, ''])
        # state (with start hook)
        self.acc = self.tl + self.acc_start + self.rx + self.table_l(row)[4:] # color(3 as '[x]') + char(1)

    # dummy
    def upd_dummy_rows(self, is_last_stage):
        n_rows = self.n_rows_last_stage if is_last_stage else self.n_rows_per_stage
        w_cols = self.calc_w_cols()
        dummy_rows = [self.table_l([self.dummy_col(w) for w in w_cols]) for _ in range(n_rows)]
        self.dummy_rows = '\n'.join(dummy_rows)
        self.n_dummy_rows = n_rows # for cursor_shift
    def upd_footer(self):
        self.footer = self.table_f(self.calc_w_cols())
    def calc_w_cols(self):
        if self.mode == 'exam':
            return [self.w_ops]
        w_cols = [self.w_start, self.w_ops, self.w_result]
        w_cols += [self.wt] * (4 if self.t_goal else 3)
        return w_cols
    def dummy_col(self, w):
        return [' '*w, 'center', w, '']

    # stage.start
    def upd_stage_start(self, stage_number, user_errors):
        # start
        if self.mode == 'exam':
            self.stage_start = self.sep
        else:
            user_errors += 1
            user_errors = '' if user_errors == 1 else f"[r]x{user_errors if user_errors < 10 else '9'}"
            self.stage_start = self.sep + c.center(f'[x]{stage_number}/{self.n_stages}{user_errors}', self.w_start) + self.sep
        # state
        self.stage = self.stage_start
        self.row_ops = ''
    # stage.op
    def upd_stage_op(self, operand, number, pls_show):
        # на новую строку если ширина закончилась (dummy уже отрисованы)
        if c.ln(self.row_ops) + self.w_op > self.w_ops:
            # upd stage:
            # +pfx
            self.stage += ' '*(self.w_ops - c.ln(self.row_ops))
            # +dummy result, timing
            row = [dummy_col(self.w_result)] + [dummy(self.wt) for _ in range(3)]
            if self.t_goal:
                row.append([' '*self.wt, 'center', self.wt, ''])
            self.stage += self.table_l(row)
            # +\n, dummy start
            self.stage += '\n' + self.table_l([[' '*self.w_start, 'center', self.w_start, '']])
            # reset current row, move cursor
            self.row_ops = ''
            self.cursor_shift(y=1)
            self.cursor_move(x=self.x_ops)
        # new operation
        operand = '' if (operand == '+' and not pls_show) else operand
        # state
        self.stage_op = c.rjust(f'[c]{operand}{number}', self.w_op)
        self.stage += self.stage_op
        self.row_ops += self.stage_op
    # stage.result
    def upd_stage_ops_pfx(self):
        self.stage_ops_pfx = ' '*(self.w_ops - c.ln(self.row_ops)) + self.sep
        self.stage += self.stage_ops_pfx
    def upd_stage_result(self, total):
        self.stage_result = '[c]'+c.center(s.tostr(total), self.w_result) + self.sep
        self.stage += self.stage_result
    # stage.timing
    def upd_stage_timing(self, t_spent, timing, is_passed, is_last_stage):
        self.n_donestages += 1 # for delta time
        if self.mode != 'exam':
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
        return self.dec_colorize_ft(ft, v_color, z_color)
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
    def dec_colorize_ft(self, ft, v_color, z_color):
        v_color, z_color = '['+v_color+']', '['+z_color+']'
        match = re.search('[1-9]\d*', ft)
        if match:
            zeros = ft[:match.start()]
            values = ft[match.start():]
            ft = z_color + zeros + v_color + values
        else:
            ft = v_color + ft
        return ft
    def calc_delta(self, spent, target, is_last_stage):
        if is_last_stage:
            return target - spent
        done_ops = self.n_donestages * self.n_ops_per_stage
        time4stage = round((target / self.n_ops) * done_ops, 2)
        delta = time4stage - spent
        return delta

    # finish
    def upd_finish(self, is_passed, end_time):
        if self.mode == 'exam':
            answer = self.answer if self.answer else 'NONE'
            if is_passed:
                msg = dedent(f'''
                    [g]Exam was passed!
                    [x]Response was: [g]{answer}
                ''').strip() + '\n'
                v_color = 'g'
            else:
                msg = dedent(f'''
                    [r]The exam was not passed:
                    [x]  Response was:      [r]{answer}
                    [x]  Correct answer is: [c]{self.total}
                    [x]Result will not be recorded in the leaderboard table.
                ''').strip() + '\n'
                v_color = 'c'
        else:
            msg = f"[{'b' if is_passed else 'c'}]Exercise was finished!"
            v_color = 'y'
        msg += f"[x]\nYour time is: {self.dec_t2ft(end_time, v_color=v_color)}"
        self.finish = self.padding(msg, [3,1,0,1])
    # leaderboard
    def upd_leaderboard(self, df, user_data):
        df_exam = df.loc[(df['is_exam'] == 1)]
        df_training = df.loc[(df['is_exam'] == 0) & (df['is_passed'] == 1)]
        df_repetitions = df.loc[(df['is_exam'] == 0) & (df['is_passed'] == 0)]
        table_exam = self.get_leaderboard_table(df_exam, 'g', user_data)
        table_training = self.get_leaderboard_table(df_training, 'b', user_data)
        table_repetitions = self.get_leaderboard_table(df_repetitions, 'x', user_data)
        leaderboard_list = self.merge_tables(table_exam, table_training, table_repetitions)
        self.leaderboard = self.padding('\n'.join(leaderboard_list),[3,0,0,0])
    def get_leaderboard_table(self, df, row_color, user_data):
        user_id = user_data['id'] if user_data else False
        user_rank = user_data['rank'] if user_data else False
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
        n_rows = df.shape[0]
        if n_rows > table_size:
            table.append(empty_record)
        # if user rank worse than 9
        if is_user_here and not is_user_found:
            table.append(self.row2rec(row, row_color, user_data))
            # if there records with rank worse than user rank
            if n_rows > user_rank:
                table.append(empty_record)
        table.append(c.z('[x]└─────────────────────────────┘'))
        return table
    def row2rec(self, row, row_color, user_data=False):
        rank, name, time, date = (
            (user_data['rank'], user_data['user_name'], user_data['time'], user_data['date'])
            if user_data else
            (row['rank'], row['user_name'], row['time'], row['date'])
        )
        color = 'y' if user_data else row_color
        rank = '99' if rank > 99 else (f'{rank} ' if rank < 10 else str(rank))
        name = name.ljust(6) if len(name) < 6 else name
        v_color = 'c' if color == 'x' else color
        time = self.dec_t2ft(time, v_color=v_color, z_color='x')
        return c.z(f'[x]│ [{color}]{rank} {name} {time}[x] {date} │')
    def merge_tables(self, exam, training, repetitions):
        table = []
        table.append(c.z('[x]  ┌─ Leaderboard ─────────────────────────────────────────────────────────────────────┐'))
        table.append(c.z('[x]  │                             ┌────────────────────── Training ─────────────────────┴─┐'))
        table.append(c.z('[x]┌─┴─ [g]EXAM PASSED[x] ─────────────┐─┴─ [b]Passed[x] ──────────────────┐─── With repetitions ──────┴─┐'))
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
