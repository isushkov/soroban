import os
import sys
import tty
import termios
import select
import re
import time
from datetime import datetime
from gtts import gTTS
from num2words import num2words
from src.config import Config
import src.helpers.fo as fo
import src.helpers.pdo as pdo
import src.helpers.colors as c
from src.helpers.cmd import cmd
from src.helpers.tui import Tui

class Run:
    def __init__(self, path, mode, user_name, target=False):
        # args/conf/fs
        self.conf = Config()
        self.path = path
        self.mode = mode or self.conf.mode
        self.user_name = user_name or conf.user_name
        self.records_columns = ['id', 'rank', 'name', 'exercise', 'is_exam', 'is_passed', 'time', 'time_seconds', 'date']
        self.prepare_fs()
        self.exercise = os.path.splitext(os.path.basename(self.path))[0]
        self.sequence = fo.txt2str(self.path)
        self.all_numbers = self.get_numbers()
        self.len_for_number = 2+len(str(max(self.all_numbers)))
        self.start_number = self.all_numbers[0]
        print(c.center(c.z(f' [y]RUNNING {self.user_name}:[c] {self.path} '), 94, '=', 'x'))
        # TODO check
        self.operands = [symbol for symbol in '+-/*' if symbol in self.sequence.split('=')[0]]
        self.operand = self.operands[0] if self.operands else None
        self.total = self.str2num(self.sequence.split('=')[1].strip())
        self.is_exam = True if self.mode == 'exam' else False
        if self.is_exam:
            self.conf.check_method = 'input'
        # tui
        self.fd = sys.stdin.fileno()
        self.term_origin = termios.tcgetattr(self.fd)
        self.term_noecho = termios.tcgetattr(self.fd)
        self.tui = Tui()
        self.tui.noecho()
        # generate sounds
        self.generate_sounds_texts()
        self.generate_sounds_numbers()
        # get records data
        self.df_records = csv.get_records()
        self.df_exercise = self.get_df_exercise()
        self.best_time_passed = self.get_best_time(passed=True)
        self.best_time_repetitions = self.get_best_time(passed=False)
        # run stage
        self.is_passed = True
        self.stage_succeed = True
        self.is_last_stage = False
        self.user_errors = 0
        self.get_ready()
        if self.is_exam:
            self.stages = [self.all_numbers]
        else:
            self.stages = [self.all_numbers[i:i+self.conf.numbers_per_stage] for i in range(1, len(self.all_numbers), self.conf.numbers_per_stage)]
        for i, stage in enumerate(self.stages):
            self.stage_number = i+1
            self.stage_numbers = self.stages[i]
            if self.is_exam:
                self.stage_numbers.pop(0)
            if self.stage_number == len(self.stages):
                self.is_last_stage = True
            self.start_number = self.run_stage()
        # finish
        self.end_time = round(time.time(), 2)
        self.end_time_formated = self.format_time(self.end_time - self.start_time)
        self.date = datetime.fromtimestamp(self.end_time).strftime('%d.%m.%y')
        self.announce_finish()
        if self.is_new_record:
            self.update_records()
        self.display_results()
        return is_passed, round(self.end_time - self.start_time, 2)

    # args/conf/fs
    def prepare_fs(self):
        cmd(f'mkdir -p ./sounds/{self.conf.lang}/numbers')
        if not fo.f_exist('./src/__records.csv'):
            cmd(f'echo {",".join(self.records_columns)} > ./src/__records.csv')
    # sounds
    def generate_sounds_texts(self):
        texts = fo.yml2dict('./src/_texts4sounds.yml')
        total = len(texts)
        for i,sound in enumerate(texts):
            path = f'sounds/{self.conf.lang}/{sound}.mp3'
            if not fo.f_exist(path):
                self.generate_sound(path, texts[sound][self.conf.lang])
            self.progress_bar('generate speech (texts)  ', total, i)
        print()
    def generate_sounds_numbers(self):
        current_sum = self.all_numbers[0]
        sum_list = [current_sum]
        for number in self.all_numbers[1:]:
            if self.operand == '+':
                current_sum += number
            elif self.operand == '-':
                current_sum -= number
            else:
                print(f'TODO: unknown operand "{self.operand}"')
                exit(1)
            sum_list.append(current_sum)
        numbers = self.all_numbers + sum_list
        for i, number in enumerate(numbers):
            path = f'sounds/{self.conf.lang}/numbers/{number}.mp3'
            if not fo.f_exist(path):
                self.generate_sound(path, num2words(number, lang=self.conf.lang))
            self.progress_bar('generate speech (numbers)', len(numbers), i)
        print()
    def generate_sound(self, path, text):
        tts = gTTS(text=text, lang=self.conf.lang)
        tts.save(path)
    def progress_bar(self, msg, total, i):
        progress = int((i + 1) / total * 62)
        done = '#' * progress
        in_progress = ('.'*(62 - progress))
        print(c.z(f'[x]>>> {msg} [{done}{in_progress}]'), end='\r', flush=True)
    def say_beep(self, sound, speed):
        self.mpv(f'sounds/{sound}.mp3', speed)
    def say_text(self, sound, speed):
        self.mpv(f'sounds/{self.conf.lang}/{sound}.mp3', speed)
    def say_number(self, sound, speed):
        path = f'sounds/{self.conf.lang}/numbers/{sound}.mp3'
        if not fo.f_exist(path):
            self.generate_sound(path, num2words(sound, lang=self.conf.lang))
        self.mpv(path, speed)
    def mpv(self, path, speed):
        if not fo.f_exist(path):
            c.p(f'[r]ERROR:[c] MPV - File not exist: {path}')
            exit(1)
        if not speed:
            return False
        cmd(f'mpv {path} --speed={speed}', strict=False, verbose4fail=False)

    # dfs
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
        c.p(f'{color}{self.mode.upper()}. [y]Get ready.[x] Start number:[c] {self.start_number}')
        self.say_text('get-ready', self.conf.spd_speech)
        self.say_text('start-number', self.conf.spd_speech)
        self.say_number(self.start_number, self.conf.spd_speech)

    # run stage
    def run_stage(self):
        total = self.start_number
        self.announce_stage()
        for number in self.stage_numbers:
            # output
            op = '' if (self.operand == '+' and not self.conf.show_plus) else self.operand
            output = f' {op}{number}'.rjust(self.len_for_number)
            self.stage_row += output
            print(output, end='', flush=True)
            # say operand
            self.say_text(self.operand, self.conf.spd_plus if self.operand == '+' else self.conf.spd_number)
            # say number
            self.say_number(number, self.conf.spd_number)
            time.sleep(self.conf.spd_delay)
            if self.operand == '+':
                total += number
            elif self.operand == '-':
                total -= number
            else:
                print(f'TODO: unknown operand "{self.operand}"')
                exit(1)
        # check stage result
        self.stage_succeed = self.check_answer(total)
        if not self.stage_succeed:
            self.is_passed = False
            if self.is_exam:
                self.tui.clear_lines(1)
                print(self.stage_row + self.get_delta_time())
                print(self.answer_line)
            else:
                self.say_beep('wrong', self.conf.spd_wrong)
                if self.user_errors < 9:
                    self.user_errors += 1
                self.tui.clear_lines(1)
                total = self.run_stage()
        else:
            self.user_errors = 0
            self.tui.clear_lines(1)
            print(self.stage_row + self.get_delta_time())
        return total

    def announce_stage(self):
        # print
        if not self.is_exam:
            stage_lenght = len(str(len(self.stages))) + 9
            stage_row =  f'[x]Stage{self.stage_number}'
            if self.user_errors:
                stage_row += f'[r].x{self.user_errors+1}[x]'
            stage_row += ':'
            self.stage_row = c.ljust(c.z(stage_row), stage_lenght)
        else:
            self.stage_row = c.z(f'[r]x{self.user_errors+1}[x]:') if self.user_errors else ''
        print(self.stage_row, end='', flush=True)
        # calc speed
        if self.stage_number == 1 and self.stage_succeed:
            speed = self.conf.spd_speech
            speed_beeps = self.conf.spd_signals
        else:
            speed = self.conf.spd_stage
            speed_beeps = self.conf.spd_start
        # say
        if not self.is_exam:
            self.say_text('stage', speed)
            self.say_number(self.stage_number, speed)
        if not self.stage_succeed:
            self.say_text('continue-with', self.conf.spd_stage_cont_txt)
            self.say_number(self.start_number, self.conf.spd_stage_cont_num)
        self.say_beep('start', speed_beeps)
        # init start time
        if self.stage_number == 1:
            self.start_time = round(time.time(), 2)
    def check_answer(self, total):
        if self.conf.check_method == 'input':
            return self.check_answer_input(total)
        return self.check_answer_yesno(total)
    def check_answer_input(self, total):
        self.stage_row = c.edgesjust(self.stage_row, f' ={total}', 75)
        print()
        if self.is_last_stage:
            msg = c.z(f'[y]Your answer: ')
            sound = 'enter-answer'
        else:
            msg = c.z(f'[y]Your stage result: ')
            sound = 'enter-stage-result'
        print(msg, end='', flush=True)
        self.say_text(sound, self.conf.spd_enter_result)
        result, valid = self.input2number(self.input())
        self.answer_line = msg + str(result)
        self.tui.clear_lines(1)
        if not valid:
            return False
        return True if result == total else False
    def input2number(self, value):
        try:
            number = float(value)
            return (int(number), True) if number.is_integer() else (number, True)
        except ValueError:
            return str(value), False
    def check_answer_yesno(self, total):
        self.stage_row = c.edgesjust(self.stage_row, f' ={total}', 75)
        self.tui.cursor_move(x=0)
        print(self.stage_row)
        self.say_text('answer' if self.is_last_stage else 'stage-result', self.conf.spd_result_txt)
        self.say_number(total, self.conf.spd_result_num)
        # menu
        gonext = 'FINISH' if self.is_last_stage else 'Continue'
        menu  = f'   [y]<Space/Enter>[c]   {gonext}\n'
        menu +=  '   [y]<a-Z>[c]           Restart the stage\n'
        menu +=  '   [y]<Esc>[c]           Exit'
        c.p(menu)
        # get key
        key = self.tui.getch()
        self.tui.clear_lines(3)
        if key in [' ', '\r', '\n']: # next stage
            return True
        elif key == '\x1b':  # Esc
            c.p('[g]Exit.')
            exit(0)
        else: # restart stage
            return False

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
        return c.z(f' [x]{self.format_time(user_time_spent)} {color}{delta_part}')
    def define_best_time(self):
        if self.is_exam:
            return self.best_time_passed if self.best_time_passed else False
        if not self.is_exam and self.is_passed:
            return self.best_time_passed if self.best_time_passed else False
        if not self.is_exam and not self.is_passed:
            return self.best_time_repetitions if self.best_time_repetitions else False
    def get_best_time_spent(self, best_time):
        if self.is_last_stage:
            return best_time
        prev_stages_count_numbers_done = self.conf.numbers_per_stage * (self.stage_number - 1)
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
        self.say_beep('end-game-passed' if self.is_passed else 'end-game', self.conf.spd_signals)
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
        self.df_records = pd.concat([self.df_records, new_df], ignore_index=True)
        self.df_exercise = self.get_df_exercise()
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
    # TODO:
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
