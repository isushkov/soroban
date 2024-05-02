import os
import re
import time
from datetime import datetime
from gtts import gTTS
from num2words import num2words
# src
from src.config import Config
import src.sequence as s
# src/view
from src.view._tui import Tui
from src.view.run import ViewRun
# src/helpers
from src.helpers.cmd import cmd
import src.helpers.fo as fo
import src.helpers.pdo as pdo
import src.helpers.colors as c

cfg = Config()
tui = Tui()
view = ViewRun()
def run(path, mode, uname, goal=False):
    view.render_title('[y]RUNNING')
    # config
    cfg.init4mode(mode)
    uname = uname or cfg.uname
    check_method = 'input' if mode == 'exam' else cfg.check_method
    # exercise
    exercise_name = os.path.splitext(os.path.basename(path))[0]
    sequence, total_provided = fo.txt2str(path).split('=')
    sequence = s.validate_sequence(sequence, exit_policy=2)
    operations = sequence.split()
    start_number = operations.pop(0)
    total = s.safe_eval(sequence)
    # reocords
    records_columns = ['id', 'rank', 'user_name', 'exercise', 'is_exam', 'is_passed', 'time', 'time_seconds', 'date']
    where = {'exercise': exercise_name, 'is_exam': '1' if mode == 'exam' else '0'}
    df_records = pdo.load('./src/__records.csv', columns=records_columns, allow_empty=True)
    df_run = pdo.filter(df_records, where=where, allow_empty=True, allow_many=True)
    timing = get_timing(df_run, uname, goal)
    # fs/sounds/view
    prepare_fs()
    tui.noecho()
    view.render_title(exercise_name, char='.')
    generate_sounds_texts()
    generate_sounds_numbers(operations)
    uname = uname or get_uname()
    view.init_params(mode, goal, uname)
    view.init_ws(sequence, cfg.num_per_stage, cfg.pls_show)
    # sounds/run
    ready(start_number)
    view.render_top(is_passed=True, timing=timing)
    start_time = round(time.time(), 2)
    is_passed = run_stages(mode, start_number, operations, check_method, timing, start_time)
    end_time = round(round(time.time(), 2) - start_time, 2)
    # finish
    view.render_finish(is_passed, end_time)
    say_beep('end-game-passed' if is_passed else 'end-game', cfg.signals_spd)
    # upd_records
    if mode == 'training' or is_passed:
        df_records = add_record(df_records, uname, exercise_name, mode, is_passed, end_time)
        user_id = df_records.index[-1]
        df_records = upd_ranks(df_records)
        pdo.save(df_records, './src/__records.csv')
        user_data = df_records.loc[user_id].to_dict()
        user_data['id'] = user_id
    else:
        user_data = False
    # leaderboard
    df = pdo.filter(df_records, where={'exercise':exercise_name}, allow_empty=True, allow_many=True)
    view.render_leaderboard(df, user_data)
    tui.echo()
    return is_passed, end_time

# run
def get_uname():
    tui.echo()
    uname = input('Please enter your name: ').strip()[:6] or '<anon>'
    tui.noecho()
def ready(start_number):
    view.render_ready(start_number)
    say_text('get-ready', cfg.speech_spd)
    say_text('start-number', cfg.speech_spd)
    say_number(start_number, cfg.speech_spd)
    input(c.z('Press [y]<Enter>[c] to start..\n'))
def run_stages(mode, start_number, operations, check_method, timing, start_time):
    is_passed = True
    user_errors = 0
    if mode == 'exam':
        stages = [operations]
    else:
        chunk = cfg.num_per_stage
        stages = [operations[i:i+chunk] for i in range(0, len(operations), chunk)]
    total = s.tonum(start_number)
    is_restart_stage = False
    for stage_number, stage_ops in enumerate(stages, start=1):
        is_last_stage = True if stage_number == len(stages) else False
        is_passed = run_stage(mode, stage_number, total, stage_ops, check_method,is_passed,
                              is_restart_stage, is_last_stage, user_errors, timing, start_time)
    return is_passed
def run_stage(mode, stage_number, total, stage_ops, check_method, is_passed,
              is_restart_stage, is_last_stage, user_errors, timing, start_time):
    # stage_start
    if mode == 'training':
        view.render_stage_start(stage_number, user_errors, oneline=True)
        say_stage_start(stage_number, total, is_restart_stage)
    # operations
    run_operations(stage_ops)
    # answer
    total = total + s.safe_eval(' '.join(stage_ops))
    if check_method == 'yes-no':
        x_curs_shift = view.render_stage_result(total, color='c', oneline=True)
        print(x_curs_shift)
        exit()
        say_text('answer' if is_last_stage else 'stage-result', cfg.res_ann_spd)
        say_number(total, cfg.res_num_spd)
        view.render_yesno(is_last_stage)
        answer = ask_yesno()
        tui.clear_lines(3)
    else:
        view.render_input(is_last_stage, oneline=True)
        sound = 'enter-answer' if is_last_stage else 'enter-stage-result'
        say_text(sound, cfg.res_entry_spd)
        answer = True if ask_input() == total else False
    # result.failed
    if not answer:
        user_errors += 1
        is_restart_stage = True
        is_passed = False
        say_beep('wrong', cfg.res_wrong_spd)
        tui.clear_lines(1)
        run_stage(mode, stage_number, total, stage_ops, check_method, is_passed,
                  is_restart_stage, is_last_stage, user_errors, timing, start_time)
    # result.ok
    now = round(time.time(), 2)
    # rewrite result
    tui.cursor_shift(x=x_curs_shift)
    tui.clear('end')
    view.render_stage_result_ok(total, color='g', oneline=True)
    view.render_stage_timing(is_passed, timing, start_time, now, oneline=True)
    return is_passed

# stage.start
def say_stage_start(stage_number, start_number, is_restart_stage):
    if stage_number == 1 and not is_restart_stage:
        speed_ann = cfg.speech_spd
        speed_beeps = cfg.signals_spd
    else:
        speed_ann = cfg.start_ann_spd
        speed_beeps = cfg.start_sig_spd
    # say
    say_text('stage', speed_ann)
    say_number(stage_number, speed_ann)
    if is_restart_stage:
        say_text('continue-with', cfg.cont_ann_spd)
        say_number(start_number, cfg.cont_num_spd)
    say_beep('start', speed_beeps)
# stage.operations
def run_operations(stage_ops):
    for operation in stage_ops:
        operand, number = s.split_operation(operation)
        view.render_stage_operation(operand, cfg.pls_show, number, oneline=True)
        speed_operand = cfg.pls_spd if operand == '+' else cfg.num_spd
        say_text(operand, speed_operand)
        say_number(number, cfg.num_spd)
        time.sleep(cfg.num_delay)
# stage.answer
def ask_yesno():
    key = tui.getch()
    if key in [' ', '\r', '\n']: # next stage
        return True
    elif key == '\x1b':  # Esc
        c.p('[g]Exit.')
        exit(0)
    else: # restart stage
        return False
def ask_input():
    tui.echo()
    answer = s.tonum(input())
    tui.noecho()
    tui.clear_lines(1)
    return answer
# stage.deltas
def get_timing(df_run, uname, goal):
    timing = {'passed':{},'repeat':{}}
    is_passed = '1'
    df = pdo.filter(df_run, where={'is_passed': is_passed}, allow_empty=True, allow_many=True)
    timing['passed']['usr'] = df2besttime(pdo.filter(df, where={'user_name': uname}, allow_empty=True, allow_many=True))
    timing['passed']['oth'] = df2besttime(pdo.filter(df, where_not={'user_name': uname}, allow_empty=True, allow_many=True))
    is_passed = '0'
    df = pdo.filter(df_run, where={'is_passed': is_passed}, allow_empty=True, allow_many=True)
    timing['repeat']['usr'] = df2besttime(pdo.filter(df, where={'user_name': uname}, allow_empty=True, allow_many=True))
    timing['repeat']['oth'] = df2besttime(pdo.filter(df, where_not={'user_name': uname}, allow_empty=True, allow_many=True))
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

# final
def add_record(df_records, uname, exercise_name, mode, is_passed, end_time):
    return pdo.addnew(df_records, {
        'rank': 0,
        'user_name': uname,
        'exercise': exercise_name,
        'is_exam': 1 if mode == 'exam' else 0,
        'is_passed': 1 if is_passed else 0,
        'time': view.dec_ft(end_time, pls=False),
        'time_seconds': end_time,
        'date': datetime.fromtimestamp(time.time()).strftime('%d.%m.%y')
    })
def upd_ranks(df):
    df = df.sort_values(by=['is_exam', 'is_passed', 'time_seconds'], ascending=[False, False, True])
    df['rank'] = range(1, len(df) + 1)
    return df

# sounds
def prepare_fs():
    cmd(f'mkdir -p ./sounds/{cfg.lang}/numbers')
def generate_sounds_texts():
    texts = fo.yml2dict('./src/_texts4sounds.yml')
    for i,sound in enumerate(texts):
        path = f'sounds/{cfg.lang}/{sound}.mp3'
        generate_sound(path, texts[sound][cfg.lang])
        progress_bar('generate speech (texts)  ', len(texts), i)
    print() # for progress_bar
def generate_sounds_numbers(operations):
    for i,operation in enumerate(operations):
        _, number = s.split_operation(operation)
        path = f'sounds/{cfg.lang}/numbers/{number}.mp3'
        generate_sound(path, num2words(number, lang=cfg.lang))
        progress_bar('generate speech (numbers)', len(operations), i)
    print() # for progress_bar
def generate_sound(path, text):
    if not fo.f_exist(path):
        tts = gTTS(text=text, lang=cfg.lang)
        tts.save(path)
def progress_bar(msg, start_number, i):
    w = view.w - len(msg) - 7
    progress = int((i + 1) / start_number * w)
    done = '#' * progress
    in_progress = '.'*(w - progress)
    print(c.z(f'[x]>>> {msg} [{done}{in_progress}]'), end='\r', flush=True)
def say_beep(sound, speed):
    mpv(f'sounds/{sound}.mp3', speed)
def say_text(sound, speed):
    mpv(f'sounds/{cfg.lang}/{sound}.mp3', speed)
def say_number(sound, speed):
    path = f'sounds/{cfg.lang}/numbers/{sound}.mp3'
    if not fo.f_exist(path):
        generate_sound(path, num2words(sound, lang=cfg.lang), lang=cfg.lang)
    mpv(path, speed)
def mpv(path, speed):
    if not fo.f_exist(path):
        raise Exception(c.z(f'[r]ERROR:[c] MPV - File not exist: {path}'))
    if not speed:
        return False
    cmd(f'mpv {path} --speed={speed}', strict=False, verbose4fail=False)
