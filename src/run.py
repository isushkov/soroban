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
    tui = Tui()
    tui.noecho()
    render = RunRender(operations)
    start_number = s.safe_eval(operations.pop(0))
    generate_sounds_texts(cfg.lang, render.w)
    generate_sounds_numbers(cfg.lang, operations, render.w)
    render.title(exercise)
    records_columns = ['id', 'rank', 'user_name', 'exercise', 'is_exam', 'is_passed', 'time', 'time_seconds', 'date']
    where = {'exercise': exercise, 'is_exam': '1' if mode == 'exam' else '0'}
    df_records = pdo.load('./src/__records.csv', columns=records_columns, empty_allowed=True)
    df_run = pdo.filter(df_records, where=where, empty_allowed=True, many_allowed=True)
    timing = get_timing(df_run, user_name, goal)
    # run
    user_name = user_name or get_user_name(tui)
    ready(cfg, render, mode, start_number)
    render.header(cfg, mode, goal)
    start_time = round(time.time(), 2)
    is_passed = run_stages(cfg,render,tui, mode, start_number, operations, check_method, timing, start_time)
    end_time = round(round(time.time(), 2) - start_time, 2)
    # finish
    render.finish(mode, is_passed, end_time)
    say_beep('end-game-passed' if is_passed else 'end-game', cfg.spd_signals)
    # upd_records
    if mode == 'training' or is_passed:
        df_records = add_record(df_records, user_name, exercise, mode, is_passed, end_time, render)
        user_id = df_records.index[-1]
        df_records = upd_ranks(df_records)
        pdo.save(df_records, './src/__records.csv')
        user_data = df_records.loc[user_id].to_dict()
        user_data['id'] = user_id
    else:
        user_data = False
    df = pdo.filter(df_records, where={'exercise':exercise}, empty_allowed=True, many_allowed=True)
    render.leaderboard(df, user_data)
    tui.echo()
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
def get_user_name(tui):
    tui.echo()
    user_name = input('Please enter your name: ').strip()[:6] or '<anon>'
    tui.noecho()
def ready(cfg, render, mode, start_number):
    render.ready(mode, start_number)
    say_text(cfg.lang, 'get-ready', cfg.spd_speech)
    say_text(cfg.lang, 'start-number', cfg.spd_speech)
    say_number(cfg.lang, start_number, cfg.spd_speech)
    input(c.z('Press [y]<Enter>[c] to start..\n'))
def run_stages(cfg, render, tui, mode, start_number, operations, check_method, timing, start_time):
    is_passed = True
    user_errors = 0
    if mode == 'exam':
        stages = [operations]
    else:
        chunk = cfg.numbers_per_stage
        stages = [operations[i:i+chunk] for i in range(0, len(operations), chunk)]
    total = s.tonum(start_number)
    is_restart_stage = False
    for stage_number, stage_ops in enumerate(stages, start=1):
        is_last_stage = True if stage_number == len(stages) else False
        is_passed = run_stage(cfg,render,tui, mode, stage_number, total, stage_ops, check_method,
                              is_passed, is_restart_stage, is_last_stage, user_errors, timing, start_time)
    return is_passed
def run_stage(cfg,render,tui, mode, stage_number, total, stage_ops, check_method,
              is_passed, is_restart_stage, is_last_stage, user_errors, timing, start_time):
    # start_stage
    if mode == 'training':
        render.start_stage(stage_number, user_errors)
        say_start_stage(stage_number, total, is_restart_stage, cfg)
    # operations
    run_operations(stage_ops, cfg, render)
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
        say_beep('wrong', cfg.spd_wrong)
        tui.clear_lines(1)
        run_stage(cfg,render,tui, mode, stage_number, total, stage_ops, check_method,
                  is_passed, is_restart_stage, is_last_stage, user_errors, timing, start_time)
    # result.ok
    render.deltas(is_passed, timing, start_time)
    return is_passed

# stage.start
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
# stage.operations
def run_operations(stage_ops, cfg, render):
    for operation in stage_ops:
        operand, number = s.split_operation(operation)
        render.operation(operand, number, cfg)
        speed_operand = cfg.spd_plus if operand == '+' else cfg.spd_number
        say_text(cfg.lang, operand, speed_operand)
        say_number(cfg.lang, number, cfg.spd_number)
        time.sleep(cfg.spd_delay)
# stage.answer
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
    answer = s.tonum(input())
    tui.noecho()
    tui.clear_lines(1)
    return answer
# stage.deltas
def get_timing(df_run, user_name, goal):
    timing = {'passed':{},'repeat':{}}
    is_passed = '1'
    df = pdo.filter(df_run, where={'is_passed': is_passed}, empty_allowed=True, many_allowed=True)
    timing['passed']['usr'] = df2besttime(pdo.filter(df, where={'user_name': user_name}, empty_allowed=True, many_allowed=True))
    timing['passed']['oth'] = df2besttime(pdo.filter(df, where_not={'user_name': user_name}, empty_allowed=True, many_allowed=True))
    is_passed = '0'
    df = pdo.filter(df_run, where={'is_passed': is_passed}, empty_allowed=True, many_allowed=True)
    timing['repeat']['usr'] = df2besttime(pdo.filter(df, where={'user_name': user_name}, empty_allowed=True, many_allowed=True))
    timing['repeat']['oth'] = df2besttime(pdo.filter(df, where_not={'user_name': user_name}, empty_allowed=True, many_allowed=True))
    timing['goal'] = goal
    return timing
def df2besttime(df):
    if df.empty:
        return False
    best_time_row = df.nsmallest(1, 'time_seconds')
    if best_time_row.empty:
        return False
    best_time_value = best_time_row['time_seconds'].iloc[0]
    return float(best_time_value)

# final.upd_records
def add_record(df_records, user_name, exercise, mode, is_passed, end_time, render):
    return pdo.addnew(df_records, {
        'rank': 0,
        'user_name': user_name,
        'exercise': exercise,
        'is_exam': 1 if mode == 'exam' else 0,
        'is_passed': 1 if is_passed else 0,
        'time': render.f_time(end_time, unary_plus=False),
        'time_seconds': end_time,
        'date': datetime.fromtimestamp(time.time()).strftime('%d.%m.%y')
    })
def upd_ranks(df):
    df = df.sort_values(by=['is_exam', 'is_passed', 'time_seconds'], ascending=[False, False, True])
    df['rank'] = range(1, len(df) + 1)
    return df
