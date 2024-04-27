import os
import re
import time
from datetime import datetime
from gtts import gTTS
from num2words import num2words
from src.config import Config
from src.run_render import RunRender
import src.sequence as s
import src.helpers.fo as fo
import src.helpers.pdo as pdo
import src.helpers.colors as c
from src.helpers.cmd import cmd
from src.helpers.tui import Tui


def run(path, mode, user_name, goal=False):
    # args/cfg/fs
    cfg = Config()
    mode = mode or cfg.mode
    user_name = user_name or cfg.user_name
    check_method = 'input' if mode == 'exam' else cfg.check_method
    exercise = os.path.splitext(os.path.basename(path))[0]
    prepare_fs(cfg.lang)
    sequence, total_provided = fo.txt2str(path).split('=')
    sequence = s.validate_sequence(sequence, exit_policy=2)
    operations = sequence.split()
    # init render
    tui = Tui()
    tui.noecho()
    render = RunRender(operations)
    render.title(user_name, exercise)
    # prepare-data
    start_number = s.safe_eval(operations.pop(0))
    generate_sounds_texts(cfg.lang, render.w)
    generate_sounds_numbers(cfg.lang, operations, render.w)
    # run
    ready(mode, start_number, cfg, render)
    render.header(mode, goal, cfg)
    start_time = round(time.time(), 2)
    is_passed = run_stages(mode, start_number, operations, goal, cfg, render, tui, check_method)
    end_time = round(time.time(), 2) - start_time
    print('end_time:',end_time)
    exit()
    # finish
    end_time_formated = format_time(end_time)
    date = datetime.fromtimestamp(time.time()).strftime('%d.%m.%y')
    announce_finish()
    if is_new_record:
        update_records()
    display_results()
    # # get records data
    # records_columns = ['id', 'rank', 'name', 'exercise', 'is_exam', 'is_passed', 'time', 'time_seconds', 'date']
    # df_records = pdo.load('./src/__records.csv', columns=records_columns, empty_allowed=True)
    # df_exercise = pdo.filter(df_records, where={'exercise':exercise})
    # get_timing()
    return is_passed, end_time

# args/cfg/fs/sounds
def prepare_fs(lang):
    cmd(f'mkdir -p ./sounds/{lang}/numbers')
def generate_sounds_texts(lang, w):
    texts = fo.yml2dict('./src/_texts4sounds.yml')
    for i,sound in enumerate(texts):
        path = f'sounds/{lang}/{sound}.mp3'
        generate_sound(path, texts[sound][lang], lang)
        progress_bar('generate speech (texts)  ', len(texts), i, w)
    print() # for progress_bar
def generate_sounds_numbers(lang, operations, w):
    for i,operation in enumerate(operations):
        _, number = s.split_operation(operation)
        path = f'sounds/{lang}/numbers/{number}.mp3'
        generate_sound(path, num2words(number, lang=lang), lang)
        progress_bar('generate speech (numbers)', len(operations), i, w)
    print() # for progress_bar
def generate_sound(path, text, lang):
    if not fo.f_exist(path):
        tts = gTTS(text=text, lang=lang)
        tts.save(path)
def progress_bar(msg, start_number, i, w):
    w = w - len(msg) - 7
    progress = int((i + 1) / start_number * w)
    done = '#' * progress
    in_progress = '.'*(w - progress)
    print(c.z(f'[x]>>> {msg} [{done}{in_progress}]'), end='\r', flush=True)
def say_beep(sound, speed):
    mpv(f'sounds/{sound}.mp3', speed)
def say_text(lang, sound, speed):
    mpv(f'sounds/{lang}/{sound}.mp3', speed)
def say_number(lang, sound, speed):
    path = f'sounds/{lang}/numbers/{sound}.mp3'
    if not fo.f_exist(path):
        generate_sound(path, num2words(sound, lang=lang), lang=lang)
    mpv(path, speed)
def mpv(path, speed):
    if not fo.f_exist(path):
        raise Exception(c.z(f'[r]ERROR:[c] MPV - File not exist: {path}'))
    if not speed:
        return False
    cmd(f'mpv {path} --speed={speed}', strict=False, verbose4fail=False)

# run
def ready(mode, start_number, cfg, render):
    render.ready(mode, start_number)
    say_text(cfg.lang, 'get-ready', cfg.spd_speech)
    say_text(cfg.lang, 'start-number', cfg.spd_speech)
    say_number(cfg.lang, start_number, cfg.spd_speech)
def run_stages(mode, start_number, operations, goal, cfg, render, tui, check_method):
    is_passed = True
    user_errors = 0
    if mode == 'exam':
        stages = [operations]
    else:
        chunk = cfg.numbers_per_stage
        stages = [operations[i:i+chunk] for i in range(0, len(operations), chunk)]
    total = s.dec(start_number)
    is_restart_stage = False
    for stage_number, stage_ops in enumerate(stages, start=1):
        is_passed = run_stage(mode, stage_number, stage_ops, cfg, render,tui,
                              check_method, is_passed, user_errors, is_restart_stage)
    return is_passed
def run_stage(mode, stage_number, stage_ops, cfg, render, tui,
              check_method, is_passed, user_errors, is_restart_stage):
    is_last_stage = True if stage_number == len(stages) else False
    # start_stage
    if mode == 'training':
        render.start_stage(stage_number, user_errors)
        say_start_stage(stage_number, total, is_restart_stage, cfg)
    # operations
    is_passed = run_operations(stage_ops, cfg, render)
    # answer
    total = total + s.safe_eval(' '.join(stage_ops))
    if cfg.check_method == 'yes-no':
        render.show_result(total)
        say_text(cfg.lang, 'answer' if is_last_stage else 'stage-result', cfg.spd_result_txt)
        say_number(cfg.lang, total, cfg.spd_result_num)
        render.ask_yesno(is_last_stage)
        answer = ask_yesno(tui)
        tui.clear_lines(3)
    else:
        render.ask_input(is_last_stage)
        sound = 'enter-answer' if is_last_stage else 'enter-stage-result'
        say_text(cfg.lang, sound, cfg.spd_enter_result)
        answer = True if ask_input(tui) == total else False
    # result.failed
    if not answer:
        user_errors += 1
        is_restart_stage = True
        is_passed = False
        # TODO
        self.say_beep('wrong', self.cfg.spd_wrong)
        run_stage(stage_number, stage_ops, cfg, render, tui, check_method, is_passed, user_errors, is_restart_stage)
    # TODO
    # result.ok
    self.say_beep('ok', self.cfg.spd_wrong)
    print(self.get_delta_time())
    return is_passed

# start_stage
def say_start_stage(stage_number, start_number, is_restart_stage, cfg):
    if stage_number == 1 and not is_restart_stage:
        speed = cfg.spd_speech
        speed_beeps = cfg.spd_signals
    else:
        speed = cfg.spd_stage
        speed_beeps = cfg.spd_start
    # say
    say_text(cfg.lang, 'stage', speed)
    say_number(cfg.lang, stage_number, speed)
    if is_restart_stage:
        say_text(cfg.lang, 'continue-with', cfg.spd_stage_cont_txt)
        say_number(cfg.lang, start_number, cfg.spd_stage_cont_num)
    say_beep('start', speed_beeps)
# operations
def run_operations(stage_ops, cfg, render):
    for operation in stage_ops:
        operand, number = s.split_operation(operation)
        render.operation(operand, number, cfg)
        say_operation(operand, number, cfg)
        time.sleep(cfg.spd_delay)
def say_operation(operand, number, cfg):
    speed_operand = cfg.spd_plus if operand == '+' else cfg.spd_number
    say_text(cfg.lang, operand, speed_operand)
    say_number(cfg.lang, number, cfg.spd_number)
# answer
def ask_yesno(tui):
    key = tui.getch()
    if key in [' ', '\r', '\n']: # next stage
        return True
    elif key == '\x1b':  # Esc
        c.p('[g]Exit.')
        exit(0)
    else: # restart stage
        return False
def ask_input(tui):
    tui.echo()
    answer = s.dec(input())
    tui.noecho()
    tui.clear_lines(1)
    return answer

# TODO
# result.ok
# timing:
#   training:
#     passed:
#       best-user: ---
#       best-other: ---
#     repeat:
#       best-user: ---
#       best-other: ---
#   exam:
#     best-user: ---
#     best-other: ---
#   goal: ---
# def get_timing():
#     self.best_time_passed = self.get_best_time(passed=True)
#     self.best_time_repetitions = self.get_best_time(passed=False)
#     pass
#     def get_best_time(self, passed):
#         df = self.df_exercise[(self.df_exercise['is_exam'] == self.is_exam) & (self.df_exercise['is_passed'] == passed)]
#         if df.empty:
#             return None
#         best_time_row = df.nsmallest(1, 'time_seconds')
#         best_time_value = best_time_row['time_seconds'].iloc[0]
#         return best_time_value
# # delta time
# def get_delta_time(self):
#     best_time = self.define_best_time()
#     if not best_time:
#         return ''
#     best_time_spent = self.get_best_time_spent(best_time)
#     user_time_spent = round(round(time.time(), 2) - self.start_time, 2)
#     delta_time = round(best_time_spent - user_time_spent, 2)
#     sfx, color = ('+', '[g]') if delta_time >= 0 else ('', '[r]')
#     delta_part =f'{sfx}{self.format_time(delta_time)}'
#     return c.z(f' [x]{self.format_time(user_time_spent)} {color}{delta_part}')
# def define_best_time(self):
#     if self.is_exam:
#         return self.best_time_passed if self.best_time_passed else False
#     if not self.is_exam and self.is_passed:
#         return self.best_time_passed if self.best_time_passed else False
#     if not self.is_exam and not self.is_passed:
#         return self.best_time_repetitions if self.best_time_repetitions else False
# def get_best_time_spent(self, best_time):
#     if self.is_last_stage:
#         return best_time
#     prev_stages_count_numbers_done = self.cfg.numbers_per_stage * (self.stage_number - 1)
#     this_stage_count_numbers_done = len(self.stage_numbers)
#     count_numbers_done = prev_stages_count_numbers_done + this_stage_count_numbers_done
#     best_time_per_number = round(best_time / (len(self.all_numbers) - 1), 2)
#     best_time_spent = round(best_time_per_number * count_numbers_done, 2)
#     return best_time_spent
# def format_time(self, seconds_total):
#     sign = "-" if seconds_total < 0 else ""
#     seconds_total = abs(seconds_total)
#     max_seconds = 99 * 60 + 99.99
#     if seconds_total >= max_seconds:
#         return sign + '99:59.99'
#     minutes = int(seconds_total // 60)
#     seconds = round(seconds_total % 60, 2)
#     if minutes >= 99:
#         minutes = 99
#         seconds = min(seconds, 59.99)
#     formatted_time = f'{sign}{minutes:02d}:{seconds:05.2f}'
#     return formatted_time

# TODO
# # finish
# def upd_rank(self):
#     self.df_exercise['sort_priority'] = self.df_exercise.apply(
#         lambda row: 0 if row['is_exam'] == 1 else (1 if row['is_passed'] == 1 else 2), axis=1
#     )
#     self.df_exercise.sort_values(by=['sort_priority', 'time_seconds'], ascending=[True, True], inplace=True)
#     self.df_exercise.drop('sort_priority', axis=1, inplace=True)
#     self.df_exercise['rank'] = range(1, len(self.df_exercise) + 1)
#     for idx in self.df_exercise.index:
#         self.df_records.at[idx, 'rank'] = self.df_exercise.at[idx, 'rank']
#     return self.df_records.loc[self.user_id, 'rank']
#
# def announce_finish(self):
#     self.is_new_record = True
#     if self.is_exam:
#         if self.is_passed:
#             msg = '[g]Exam was passed!'
#         else:
#             msg = '[r]The exam was not passed.'
#             self.is_new_record = False
#     else:
#          msg = '[g]Exercise was finished!'
#     c.p(f'{msg}[c] Your time is: [y]{self.end_time_formated}')
#     self.say_beep('end-game-passed' if self.is_passed else 'end-game', self.cfg.spd_signals)
# def update_records(self):
#     if not self.user_name:
#         self.tui.echo()
#         self.user_name = input('Please enter your name: ').strip()[:6] or '<anon>'
#         self.tui.noecho()
#     new_df = pd.DataFrame([{
#         'rank': 0,
#         'name': self.user_name,
#         'exercise': self.exercise,
#         'is_exam': 1 if self.is_exam else 0,
#         'is_passed': 1 if self.is_passed else 0,
#         'time': self.end_time_formated,
#         'time_seconds': round(self.end_time - self.start_time, 2),
#         'date': self.date
#     }])
#     self.df_records = self.df_records.dropna(axis=1, how='all')
#     self.df_records = pdo.concat([self.df_records, new_df], ignore_index=True)
#     self.df_exercise = pdo.filter(self.df_records, where={'exercise':self.exercise},
#                                   empty_allowed=True, many_allowed=True)
#
#
#     self.user_id = self.df_records.index[-1]
#     self.user_rank = self.upd_rank()
#     # save
#     pdo.save(df_records, 'data/_records.csv')
#
# def display_results(self):
#     df = self.df_exercise
#     df_exam = df.loc[(df['is_exam'] == 1)]
#     df_training = df.loc[(df['is_exam'] == 0) & (df['is_passed'] == 1)]
#     df_repetitions = df.loc[(df['is_exam'] == 0) & (df['is_passed'] == 0)]
#     table_exam = self.get_leaderboard_table(df_exam, '[g]')
#     table_training = self.get_leaderboard_table(df_training, '[b]')
#     table_repetitions = self.get_leaderboard_table(df_repetitions, '[x]')
#     table = self.merge_tables(table_exam, table_training, table_repetitions)
#     # print
#     print('')
#     for line in table:
#         print('   '+line)
#     print('')
# # TODO:
# def get_leaderboard_table(self, df, row_color):
#     table = []
#     table_size=9
#     if df.empty:
#         table.append(c.z('[x]│ None                        │'))
#         table.append(c.z('[x]└─────────────────────────────┘'))
#         return table
#     # find user in df
#     is_user_here = self.is_new_record and not df[df.index == self.user_id].empty
#     # first_9
#     is_user_found = False
#     for i, row in df.head(table_size).iterrows():
#         if is_user_here and i == self.user_id:
#             is_user_found = True
#             table.append(self.row2rec(row, row_color, is_user=True))
#             continue
#         table.append(self.row2rec(row, row_color, is_user=False))
#     # if records is more than table_size
#     empty_record = c.z('[x]│ .. ...         ... ........ │')
#     rows_count = df.shape[0]
#     if rows_count > table_size:
#         table.append(empty_record)
#     # if user rank worse than 9
#     if is_user_here and not is_user_found:
#         table.append(self.row2rec(row, row_color, is_user=True))
#         # if there records with rank worse than user rank
#         if rows_count > self.user_rank:
#             table.append(empty_record)
#     table.append(c.z('[x]└─────────────────────────────┘'))
#     return table
# def row2rec(self, row, row_color, is_user):
#     rank, name, time = (
#         (self.user_rank, self.user_name, self.end_time_formated)
#         if is_user else
#         (row['rank'], row['name'], row['time'])
#     )
#     rank = '99' if rank > 99 else (f'{rank} ' if rank < 10 else str(rank))
#     name = name.ljust(6) if len(name) < 6 else name
#     color = '[y]' if is_user else row_color
#     return c.z(f'[x]│ {color}{rank} {name} {time}[x] {self.date} │')
#
# def merge_tables(self, exam, training, repetitions):
#     table = []
#     table.append(c.z('[x]  ┌─ Leaderboard ─────────────────────────────────────────────────────────────────────┐'))
#     table.append(c.z('[x]  │                             ┌────────────────────── Training ─────────────────────┴─┐'))
#     table.append(c.z('[x]┌─── [g]EXAM PASSED[x] ─────────────┐─┴─ [b]Passed[x] ──────────────────┐─── With repetitions ──────┴─┐'))
#     max_length = max(len(exam), len(training), len(repetitions))
#     sep = ' '*30
#     for i in range(max_length):
#         exm = exam[i] if i < len(exam) else sep
#         trg = training[i] if i < len(training) else sep
#         rep = repetitions[i] if i < len(repetitions) else sep
#         # eettrr  eettrr
#         #   ttrr  eett
#         #     rr  ee
#         if exm.strip() and trg.strip():
#             trg = self.cut_line(trg)
#         if trg.strip() and rep.strip():
#             rep = self.cut_line(rep)
#         # eettrr
#         # ee  rr
#         #     rr
#         # if not trg.strip() and rep.strip():
#         #     trg = trg[1:]
#         new_line = exm + trg + rep
#         table.append(new_line)
#     return table
# def cut_line(self, line):
#     return c.z('[x]'+line[6:])
