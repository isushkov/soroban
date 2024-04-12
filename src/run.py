from src.helpers.fo import Fo as fo
from src.helpers.fexit import fexit
from src.helpers.cmd import Cmd as cmd
from src.helpers.colors import *
from src.config import Config
from gtts import gTTS
from num2words import num2words
import sys
import termios
import tty
import re
import time
from datetime import datetime
import pandas as pd

class Run:
    def __init__(self, exercise):
        print(c_center(cz(f' [y]RUNNING {exercise} '), 94, '=', 'x'))
        # preinit
        self.exercise = exercise
        self.filename = f'data/{exercise}.txt'
        self.sequence = fo.txt2str(self.filename)
        self.all_numbers = self.get_numbers()
        self.len_for_number = 2+len(str(max(self.all_numbers)))
        self.start_number = self.all_numbers[0]
        self.operations = re.findall(r'\s([+\-*/])\s', self.sequence.split('=')[0])
        self.operation_char = self.operations[0] if self.operations else None # TODO: plus-minus
        self.total = self.get_total()
        self.c = Config()
        self.is_exam = True if self.c.mode == 'exam' else False
        # prepare fs
        self.records_columns = ['id', 'rank', 'name', 'exercise', 'is_exam', 'is_passed', 'time', 'time_seconds', 'date']
        self.prepare_fs()
        # generate sounds
        self.generate_sounds_texts()
        self.generate_sounds_numbers()
        # get records data
        self.df_records = self.get_df_records()
        self.df_exercise = self.get_df_exercise()
        self.best_time_passed = self.get_best_time(passed=True)
        self.best_time_repetitions = self.get_best_time(passed=False)
        # start
        self.is_passed = True
        self.get_ready()
        self.stages = [self.all_numbers[i:i+self.c.numbers_per_stage] for i in range(1, len(self.all_numbers), self.c.numbers_per_stage)]
        # TODO: without stages
        # run stage
        self.stage_result = True
        self.user_errors = 0
        self.is_last_stage = False
        for i, stage in enumerate(self.stages):
            self.stage_number = i+1
            self.stage_numbers = self.stages[i]
            if self.stage_number == len(self.stages):
                self.is_last_stage = True
            self.start_number = self.run_stage()
        # finish
        self.end_time = round(time.time(), 2)
        self.end_time_formated = self.format_time(self.end_time - self.start_time)
        self.date = datetime.fromtimestamp(self.end_time).strftime('%d.%m.%y')
        print(cz(f'[g]Exercise was finished![c] your time is: [y]{self.end_time_formated}'))
        self.say_beep('end-game-passed' if self.is_passed else 'end-game', self.c.spd_signals)
        # update records
        if self.is_exam and not self.is_passed:
            print(cz('[y]NOTE:[c] You have [r]not passed the exam[c], the result will not be saved.'))
            self.user_id = False
            self.user_rank = False
        else:
            user_name = input('Please enter your name: ').strip()
            self.user_name = user_name[:6] if user_name else '<anon>'
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
            self.df_records = pd.concat([self.df_records, new_df], ignore_index=True)
            self.df_exercise = self.get_df_exercise()
            self.user_id = self.df_records.index[-1]
            self.user_rank = self.upd_rank()
            # save
            tmp_df = self.df_records.reset_index().rename(columns={'index': 'id'})
            tmp_df.to_csv('data/_records.csv', index=False)
        # leaderboard
        self.display_results()
        # TODO: would you like to repeat?

    # preinit
    def get_numbers(self):
        return [int(num) for num in re.findall(r'\d+', self.sequence.split('=')[0])]
    def get_total(self):
        if self.operation_char == '+':
            total_calculated = sum(self.all_numbers)
        else:
            # TODO
            fexit('TODO: unknown operations')
        total_provided = int(self.sequence.split('=')[1].strip())
        if total_calculated != total_provided:
            fexit(cz('[r]FAIL:[c] Mismatch between [y]calculated total[c] and [y]provided total[c].'))
        total = total_calculated
        return total
    def prepare_fs(self):
        cmd.run(f'mkdir -p ./sounds/{self.c.lang}/numbers')
        cmd.run('mkdir -p ./data')
        if not fo.f_exist('config.yml'):
            cmd.run('copy ./examples/config.yml ./config.yml')
        if not fo.f_exist('./data/_records.csv'):
            cmd.run(f'echo {",".join(self.records_columns)} > data/_records.csv')

    # sounds
    def generate_sounds_texts(self):
        texts = fo.yml2dict('./src/texts4sounds.yml')
        total = len(texts)
        for i,sound in enumerate(texts):
            path = f'sounds/{self.c.lang}/{sound}.mp3'
            if not fo.f_exist(path):
                self.generate_sound(path, texts[sound][self.c.lang])
            self.progress_bar('generate speech (texts)  ', total, i)
        print()
    def generate_sounds_numbers(self):
        total = len(self.all_numbers)
        for i, number in enumerate(self.all_numbers):
            path = f'sounds/{self.c.lang}/numbers/{number}.mp3'
            if not fo.f_exist(path):
                self.generate_sound(path, num2words(number, lang=self.c.lang))
            self.progress_bar('generate speech (numbers)', total, i)
        print()
    def generate_sound(self, path, text):
        tts = gTTS(text=text, lang=self.c.lang)
        tts.save(path)
    def progress_bar(self, msg, total, i):
        progress = int((i + 1) / total * 62)
        done = '#' * progress
        in_progress = ('.'*(62 - progress))
        print(cz(f'[x]>>> {msg} [{done}{in_progress}]'), end='\r', flush=True)

    def say_beep(self, sound, speed):
        self.mpv(f'sounds/{sound}.mp3', speed)
    def say_text(self, sound, speed):
        self.mpv(f'sounds/{self.c.lang}/{sound}.mp3', speed)
    def say_number(self, sound, speed):
        path = f'sounds/{self.c.lang}/numbers/{sound}.mp3'
        if not fo.f_exist(path):
            self.generate_sound(path, num2words(sound, lang=self.c.lang))
        self.mpv(path, speed)
    def mpv(self, path, speed):
        if not speed:
            return False
        cmd.run(f'mpv {path} --speed={speed}', strict=False, verbose4fail=False)

    # dfs
    def get_df_records(self):
        try:
            df = pd.read_csv('data/_records.csv')
            df = df.rename(columns=lambda x: x.strip())
            df = df.apply(lambda col: col.apply(lambda x: x.strip() if isinstance(x, str) else x))
            df.set_index('id', inplace=True)
            return df
        except FileNotFoundError:
            return pd.DataFrame(columns=self.records_columns).set_index('id')
    def get_best_time(self, passed):
        df = self.df_exercise[(self.df_exercise['is_exam'] == self.is_exam) & (self.df_exercise['is_passed'] == passed)]
        if df.empty:
            return None
        best_time_row = df.nsmallest(1, 'time_seconds')
        best_time_value = best_time_row['time_seconds'].iloc[0]
        return best_time_value
    def get_df_exercise(self):
        return self.df_records[self.df_records['exercise'] == self.exercise].copy()
    def upd_rank(self):
        self.df_exercise['sort_priority'] = self.df_exercise.apply(
            lambda row: 0 if row['is_exam'] == 1 else (1 if row['is_passed'] == 1 else 2), axis=1
        )
        self.df_exercise.sort_values(by=['sort_priority', 'time_seconds'], ascending=[True, True], inplace=True)
        self.df_exercise.drop('sort_priority', axis=1, inplace=True)
        self.df_exercise['rank'] = range(1, len(self.df_exercise) + 1)
        for idx in self.df_exercise.index:
            self.df_records.at[idx, 'rank'] = self.df_exercise.at[idx, 'rank']
        return self.df_records.loc[self.user_id, 'rank']

    # ready
    def get_ready(self):
        color = '[r]' if self.is_exam else '[g]'
        print(cz(f'{color}{self.c.mode.upper()}. [y]Get ready.[x] Start number:[c] {self.start_number}'))
        self.say_text('get-ready', self.c.spd_speech)
        self.say_text('start-number', self.c.spd_speech)
        self.say_number(self.start_number, self.c.spd_speech)

    # run stage
    def run_stage(self):
        total = self.start_number
        self.announcement_stage()
        for number in self.stage_numbers:
            output = f' {self.operation_char}{number}'.rjust(self.len_for_number)
            self.stage_row += output
            print(output, end='', flush=True)
            self.say_number(number, self.c.spd_number)
            time.sleep(self.c.spd_delay)
            if self.operation_char == '+':
                total += number
            else:
                fexit(f'TODO: unknown operation "{self.operation_char}"')
        # check stage result
        self.stage_result = self.check_stage_result(total)
        if not self.stage_result:
            self.is_passed = False
            if self.user_errors < 9:
                self.user_errors += 1
            total = self.run_stage()
        else:
            self.user_errors = 0
            print(self.stage_row + self.get_delta_time())
        return total
    def announcement_stage(self):
        speed = self.c.spd_speech if self.stage_number == 1 else self.c.spd_stage
        speed_beeps = self.c.spd_signals if self.stage_number == 1 else self.c.spd_start
        stage_lenght = len(str(len(self.stages))) + 10
        pfx = f'[r].x{self.user_errors+1}[x]:' if self.user_errors else ':'
        self.stage_row = cz(f'[x]Stage{self.stage_number}{pfx}'.ljust(stage_lenght))
        print(self.stage_row, end='', flush=True)
        self.say_text('stage', speed)
        self.say_number(self.stage_number, speed)
        if not self.stage_result:
            self.say_text('continue-with', speed)
            self.say_number(self.start_number, speed)
        self.say_beep('start-beeps', speed_beeps)
        if self.stage_number == 1:
            self.start_time = round(time.time(), 2)
    def check_stage_result(self, total):
        # if input
        if self.is_exam or self.c.check_method == 'input':
            fexit('TODO: check_method input')
            return False
        # if yes-no
        total_str = f' ={total}'
        output = self.get_filled_center(remove_colors(self.stage_row), remove_colors(total_str), 94-19) + total_str
        self.stage_row += output
        print(output)
        self.say_text('answer' if self.is_last_stage else 'stage-result', self.c.spd_result)
        self.say_number(total, self.c.spd_result)
        if self.is_last_stage: print(cz('   [y]<Space/Enter>[c]   FINISH'))
        else:                  print(cz('   [y]<Space/Enter>[c]   Continue'))
        print(cz('   [y]<Other-key>[c]     Restart the stage'))
        print(cz('   [y]<Esc>      [c]     Exit'))
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        if key in [' ', '\r', '\n']: # next stage
            self.clean_output(4)
            return True
        elif key == '\x1b':  # Esc
            fexit()
        else: # restart stage
            self.clean_output(4)
            return False
    def get_filled_center(self, x, y, len_line, fill_char=' '):
        len_center  = len_line - len(x) - len(y)
        return len_center * fill_char
    def clean_output(self, count_lines):
        for _ in range(count_lines):
            sys.stdout.write('\x1b[1A')
            sys.stdout.write('\x1b[2K')

    # delta time
    def get_delta_time(self):
        best_time = self.define_best_time()
        if not best_time:
            return ''
        best_time_spent = self.get_best_time_spent(best_time)
        user_time_spent = round(round(time.time(), 2) - self.start_time, 2)
        delta_time = round(best_time_spent - user_time_spent, 2)
        sfx, color = ('+', '[g]') if delta_time >= 0 else ('', '[r]')
        delta_part =f'{sfx}{self.format_time(delta_time)}'
        return cz(f' [x]{self.format_time(user_time_spent)} {color}{delta_part}')
    def define_best_time(self):
        # если это exam (всегда без ошибок)
        if self.is_exam:
            # но рекорда еще нет
            if not self.best_time_passed:
                return False
            return self.best_time_passed
        # если это training ошибок пока не сделано
        if not self.is_exam and self.is_passed:
            # но рекорда еще нет
            if not self.best_time_passed:
                return False
            return self.best_time_passed
        # если это training, есть ошибки
        if not self.is_exam and not self.is_passed:
            # но рекорда еще нет
            if not self.best_time_repetitions:
                return False
            return self.best_time_repetitions
    def get_best_time_spent(self, best_time):
        if self.is_last_stage:
            return best_time
        prev_stages_count_numbers_done = self.c.numbers_per_stage * (self.stage_number - 1)
        this_stage_count_numbers_done = len(self.stage_numbers)
        count_numbers_done = prev_stages_count_numbers_done + this_stage_count_numbers_done
        best_time_per_number = round(best_time / (len(self.all_numbers) - 1), 2)
        best_time_spent = round(best_time_per_number * count_numbers_done, 2)
        return best_time_spent
    def format_time(self, seconds_total):
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
    # TODO:
    def get_leaderboard_table(self, df, row_color):
        table = []
        table_size=9
        if df.empty:
            table.append(cz('[x]│ None                        │'))
            table.append(cz('[x]└─────────────────────────────┘'))
            return table
        # find user in df
        is_user_here = False if df[df.index == self.user_id].empty else True
        # first_9
        is_user_found = False
        for i, row in df.head(table_size).iterrows():
            if is_user_here and i == self.user_id:
                is_user_found = True
                table.append(self.row2rec(row, row_color, is_user=True))
                continue
            table.append(self.row2rec(row, row_color, is_user=False))
        # if records is more than table_size
        empty_record = cz('[x]│ .. ...         ... ........ │')
        rows_count = df.shape[0]
        if rows_count > table_size:
            table.append(empty_record)
        # if user rank worse than 9
        if is_user_here and not is_user_found:
            table.append(self.row2rec(row, row_color, is_user=True))
            # if there records with rank worse than user rank
            if rows_count > self.user_rank:
                table.append(empty_record)
        table.append(cz('[x]└─────────────────────────────┘'))
        return table
    def row2rec(self, row, row_color, is_user):
        if is_user:
            rank, name, time = self.user_rank, self.user_name, self.end_time_formated
        else:
            rank, name, time = row['rank'], row['name'], row['time']
        if rank > 99:
            rank = '99'
        elif rank < 10:
            rank = f'{rank} '
        if len(name) < 6:
            name = name.ljust(6)
        color = '[y]' if is_user else row_color
        return cz(f'[x]│ {color}{rank} {name} {time}[x] {self.date} │')

    def merge_tables(self, exam, training, repetitions):
        table = []
        table.append(cz('[x]  ┌─ Leaderboard ───────────────────────────────────────────┐'))
        table.append(cz('[x]  │                             ┌─────────────────────── Training ──────────────────────┐'))
        table.append(cz('[x]┌─── [g]EXAM PASSED[x] ─────────────┐─┴─ [b]Passed[x] ──────────────────┐─── With repetitions ──────┴─┐'))
        # body
        max_length = max(len(exam), len(training), len(repetitions))
        for i in range(max_length):
            exm = exam[i] if i < len(exam) else ''
            trg = training[i] if i < len(training) else ''
            rep = repetitions[i] if i < len(repetitions) else ''
            sep = ' '*30
            # 100
            if exm and not trg and not rep:
                new_line = exm
            # 101
            if exm and not trg and rep:
                new_line = exm + sep + rep
            # 110
            if exm and trg and not rep:
                new_line = cz(exm + '[x]'+trg[6:])
            # 111
            if exm and trg and rep:
                new_line = cz(exm + '[x]'+trg[6:] + '[x]'+rep[6:])
            # 001
            if not exm and not trg and rep:
                new_line = sep + sep + rep
            # 010
            if not exm and trg and not rep:
                new_line = sep + trg
            # 011
            if not exm and trg and rep:
                new_line = cz(sep + trg + '[x]'+rep[6:])
            table.append(new_line)
        return table
