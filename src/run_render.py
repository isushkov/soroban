import shutil
from functools import reduce
import src.sequence as s
import src.helpers.colors as c

class RunRender():
    def __init__(self, operations):
        self.operations = operations[1:]
        self.w, _ = shutil.get_terminal_size()
        self.tab = ' '
        self.sep = ' '
        self.start_stage_max_len = len('Stage99 x2:')
        self.operation_max_len = len(max(operations, key=len)) + 1
        self.result_max_len = len(s.num2str(reduce(s.get_resNmaxres, operations, (operations[0],0))[1]))
        self.df_empty = '--:--:--'
        self.len_dt = len(self.df_empty)
    # render
    def title(self, user_name, exercise):
        return print(c.center(c.z(f' [y]RUNNING {user_name}:[c] {exercise} '), self.w, '=', 'x'))
    def ready(self, mode, start_number):
        color = '[r]' if mode == 'exam' else '[g]'
        c.p(f'{color}{mode.upper()}. [y]Get ready.[x] Start number:[c] {start_number}')
    def header(self, mode, goal, cfg):
        sep = ' '
        start_stage = ' '.ljust(self.start_stage_max_len)
        operations = 'Operations'.ljust(cfg.numbers_per_stage * self.operation_max_len)
        result = 'Result'.ljust(self.result_max_len)
        dt_target = 'Δt.goal'.center(self.len_dt)
        dt_user   = 'Δt.user'.center(self.len_dt)
        dt_other  = 'Δt.other'.center(self.len_dt)
        dts = [dt_target] + [dt_user, dt_other] if goal else [dt_user, dt_other]
        c.p('[x]'+ sep.join([start_stage, operations, result] + dts))
    def start_stage(self, stage_number, user_errors):
        user_errors = f' [r]x{min(user_errors+1, 9)}' if user_errors else ''
        render = c.ljust(c.z(f'[x]Stage{min(stage_number, 99)}{user_errors}:', 11))
        print(render, end='', flush=True)
    def operation(self, operand, number, cfg):
        operand = '' if (operand == '+' and not cfg.show_plus) else operand
        render = f' {operand}{number}'.rjust(self.operation_max_len)
        print(render, end='', flush=True)
    def result(self):
        pass
        render = c.edgesjust(self.stage_row, f' ={result}', 75)
        print(render)
    def delta(self):
        pass
    def ask_input(self):
        pass
    def ask_yesno(self, is_last_stage):
        # render menu
        menu  = f"   [y]<Space/Enter>[c]   {'FINISH' if is_last_stage else 'Continue'}\n"
        menu +=  "   [y]<a-Z>[c]           Restart the stage\n"
        menu +=  "   [y]<Esc>[c]           Exit"
        return c.z(menu)
    def leaderboard(self):
        pass

    # format
    def f_time(self, seconds_total):
        sign = "-" if seconds_total < 0 else ""
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
    def announce_finish(self):
        self.is_new_record = True
        if self.is_exam:
            if self.is_passed:
                msg = '[g]Exam was passed!'
            else:
                msg = '[r]The exam was not passed.'
                self.is_new_record = False
        else:
             msg = '[g]Exercise was finished!'
        c.p(f'{msg}[c] Your time is: [y]{self.end_time_formated}')
        self.say_beep('end-game-passed' if self.is_passed else 'end-game', self.cfg.spd_signals)
    def update_records(self):
        if not self.user_name:
            self.tui.echo()
            self.user_name = input('Please enter your name: ').strip()[:6] or '<anon>'
            self.tui.noecho()
        new_df = pd.DataFrame([{
            'rank': 0,
            'name': self.user_name,
            'exercise': self.exercise,
            'is_exam': 1 if self.is_exam else 0,
            'is_passed': 1 if self.is_passed else 0,
            'time': self.end_time_formated,
            'time_seconds': round(self.end_time - self.start_time, 2),
            'date': self.date
        }])
        self.df_records = self.df_records.dropna(axis=1, how='all')
        self.df_records = pdo.concat([self.df_records, new_df], ignore_index=True)
        self.df_exercise = pdo.filter(self.df_records, where={'exercise':self.exercise},
                                      empty_allowed=True, many_allowed=True)


        self.user_id = self.df_records.index[-1]
        self.user_rank = self.upd_rank()
        # save
        pdo.save(df_records, 'data/_records.csv')

    def display_results(self):
        df = self.df_exercise
        df_exam = df.loc[(df['is_exam'] == 1)]
        df_training = df.loc[(df['is_exam'] == 0) & (df['is_passed'] == 1)]
        df_repetitions = df.loc[(df['is_exam'] == 0) & (df['is_passed'] == 0)]
        table_exam = self.get_leaderboard_table(df_exam, '[g]')
        table_training = self.get_leaderboard_table(df_training, '[b]')
        table_repetitions = self.get_leaderboard_table(df_repetitions, '[x]')
        table = self.merge_tables(table_exam, table_training, table_repetitions)
        # print
        print('')
        for line in table:
            print('   '+line)
        print('')

    def get_leaderboard_table(self, df, row_color):
        table = []
        table_size=9
        if df.empty:
            table.append(c.z('[x]│ None                        │'))
            table.append(c.z('[x]└─────────────────────────────┘'))
            return table
        # find user in df
        is_user_here = self.is_new_record and not df[df.index == self.user_id].empty
        # first_9
        is_user_found = False
        for i, row in df.head(table_size).iterrows():
            if is_user_here and i == self.user_id:
                is_user_found = True
                table.append(self.row2rec(row, row_color, is_user=True))
                continue
            table.append(self.row2rec(row, row_color, is_user=False))
        # if records is more than table_size
        empty_record = c.z('[x]│ .. ...         ... ........ │')
        rows_count = df.shape[0]
        if rows_count > table_size:
            table.append(empty_record)
        # if user rank worse than 9
        if is_user_here and not is_user_found:
            table.append(self.row2rec(row, row_color, is_user=True))
            # if there records with rank worse than user rank
            if rows_count > self.user_rank:
                table.append(empty_record)
        table.append(c.z('[x]└─────────────────────────────┘'))
        return table
    def row2rec(self, row, row_color, is_user):
        rank, name, time = (
            (self.user_rank, self.user_name, self.end_time_formated)
            if is_user else
            (row['rank'], row['name'], row['time'])
        )
        rank = '99' if rank > 99 else (f'{rank} ' if rank < 10 else str(rank))
        name = name.ljust(6) if len(name) < 6 else name
        color = '[y]' if is_user else row_color
        return c.z(f'[x]│ {color}{rank} {name} {time}[x] {self.date} │')

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
