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
from src.view.run import ViewRun
# src/helpers
from src.helpers.cmd import cmd
import src.helpers.fo as fo
import src.helpers.pdo as pdo
import src.helpers.colors as c

def run(path, mode, uname, goal=False):
    cnf = Config()
    view = ViewRun(cnf.w)
    # config
    cnf.init4mode(mode)
    uname = uname or cnf.uname
    check_method = 'input' if mode == 'exam' else cnf.check_method
    # exercise
    exercise_name = os.path.splitext(os.path.basename(path))[0]
    sequence, total_provided = fo.txt2str(path).split('=')
    sequence = s.validate_sequence(sequence, exit_policy=2)
    ops = sequence.split()
    start_number = ops.pop(0)
    total = s.safe_eval(sequence)
    # reocords
    records_columns = ['id', 'rank', 'user_name', 'exercise', 'is_exam', 'is_passed', 'time', 'date']
    where = {'exercise': exercise_name, 'is_exam': 1 if mode == 'exam' else 0}
    df_records = pdo.load('./src/__records.csv', columns=records_columns, allow_empty=True)
    df_run = pdo.filter(df_records, where=where, allow_empty=True, allow_many=True)
    timing = get_timing(df_run, uname, goal)
    # view
    view.noecho()
    view.render_title(f'[y]RUNNING {exercise_name}')
    uname = uname or get_uname(view)
    view.init_params(mode, goal, uname, sequence, cnf.ops_per_stage, cnf.pls_show)
    # fs/sounds
    prepare_fs(cnf.lang)
    generate_sounds_texts(view.w, cnf.lang)
    generate_sounds_numbers(view.w, cnf.lang, ops)
    # run
    view.render_top(timing)
    start_time, is_passed = run_stages(cnf,view, mode, start_number, ops, check_method, timing)
    end_time = round(round(time.time(), 2) - start_time, 2)
    # finish
    view.render_finish(is_passed, end_time)
    say_beep('end-game-passed' if is_passed else 'end-game', cnf.signals_spd)
    # upd_records
    if is_passed or mode == 'training':
        df_records = add_record(df_records, uname, exercise_name, mode, is_passed, end_time)
        user_id = df_records.index[-1]
        df_records = upd_ranks(df_records, exercise_name)
        pdo.save(df_records, './src/__records.csv')
        user_data = df_records.loc[user_id].to_dict()
        user_data['id'] = user_id
    else:
        user_data = False
    # leaderboard
    df = pdo.filter(df_records, where={'exercise':exercise_name}, allow_empty=True, allow_many=True)
    df = df.sort_values(by='rank', ascending=True)
    view.render_leaderboard(df, user_data)
    view.echo()
    return is_passed, end_time

# run
def get_uname(view):
    view.echo()
    view.disp_uname_note()
    uname = input('Please enter your name: ').strip()[:6] or '<anon>'
    view.noecho()
    return uname
def run_stages(cnf,view, mode, start_number, ops, check_method, timing):
    is_passed = True
    user_errors = 0
    if mode == 'exam':
        stages = [ops]
    else:
        chunk = cnf.ops_per_stage
        stages = [ops[i:i+chunk] for i in range(0, len(ops), chunk)]
    is_restart_stage = False
    total = s.tonum(start_number)
    start_time = None
    for stage_number, stage_ops in enumerate(stages, start=1):
        is_last_stage = True if stage_number == len(stages) else False
        total, is_passed, start_time = run_stage(cnf,view, mode, stage_number, total, stage_ops, check_method,is_passed,
                                             is_restart_stage, is_last_stage, user_errors, timing, start_time)
    return start_time, is_passed
def run_stage(cnf,view, mode, stage_number, total, stage_ops, check_method, is_passed,
              is_restart_stage, is_last_stage, user_errors, timing, start_time):
    # dummny
    view.render_dummy_rows(is_last_stage)
    view.render_footer()
    # start
    view.cursor_shift(y=-view.n_dummy_rows-1)
    view.cursor_move(x=0)
    view.render_stage_start(stage_number, user_errors, end='', flush=True)
    if stage_number == 1 and not is_restart_stage:
        # menu.ready
        view.cursor_shift(y=view.n_dummy_rows-1)
        view.render_ready(total)
        say_text(cnf.lang, 'get-ready', cnf.speech_spd)
        say_text(cnf.lang, 'start-number', cnf.speech_spd)
        say_number(cnf.lang, total, cnf.speech_spd)
    # start continue
    if mode == 'training':
        # say "stage_number is N" (+"continue-with N" if needed)
        say_stage_start(cnf, stage_number, total, is_restart_stage)
    # menu.ready continue
    if stage_number == 1 and not is_restart_stage:
        input()
        view.clear_menu(view.ready)
        # cursor back
        view.cursor_shift(y=-view.n_dummy_rows-1)
        view.cursor_move(x=view.x_ops)
        # say bip-bip-bip and start
        say_beep('start', cnf.signals_spd)
        start_time = round(time.time(), 2)
    # ops
    run_ops(cnf,view, stage_ops, stage_number, is_restart_stage)
    total_bac = total
    total = total + s.safe_eval(' '.join(stage_ops))
    # menu.yes-no
    if check_method == 'yes-no':
        # result (for yes-no)
        view.render_stage_ops_pfx(end='', flush=True)
        view.render_stage_result(total, end='', flush=True)
        say_text(cnf.lang, 'answer' if is_last_stage else 'stage-result', cnf.res_ann_spd)
        say_number(cnf.lang, total, cnf.res_num_spd)
        view.render_yesno(is_last_stage)
        is_correct_answer = view.menu_yesno()
        view.clear_menu(view.yesno)
    # menu.input
    else:
        view.render_input(total, is_last_stage)
        sound = 'enter-answer' if is_last_stage else 'enter-stage-result'
        say_text(cnf.lang, sound, cnf.res_entry_spd)
        answer = view.menu_input()
        view.clear_menu(view.input)
        view.answer = answer # for finish msg
        is_correct_answer = True if s.tonum(answer, allow2fail=True) == total else False
    # wrong
    if not is_correct_answer:
        is_passed = False
        if mode == 'exam':
            return total, is_passed, start_time
        user_errors += 1
        is_restart_stage = True
        say_beep('wrong', cnf.res_wrong_spd)
        # clear current stage rows
        view.clear_lines(view.n_dummy_rows+1)
        if view.calls_top == 1: # upd top when fail only once
            # clear done stages, clear top
            view.clear_lines(view.n_donestages*view.n_rows_per_normal_stage)
            view.clear_lines(3) # clear top
            # render top with new data and disp donestages
            view.render_top(timing)
            view.disp_donestages()
        return run_stage(cnf,view, mode, stage_number, total_bac, stage_ops, check_method, is_passed,
                         is_restart_stage, is_last_stage, user_errors, timing, start_time)
    # correct
    if mode == 'training':
        # result (for input) - dont print, just sync with yes-no
        if check_method == 'input':
            view.upd_stage_ops_pfx()
            view.upd_stage_result(total)
        # timing
        t_spent = round(time.time(), 2) - start_time
        # clear stage/disp stage + add timing
        view.clear_lines(view.n_dummy_rows+1)
        view.disp_stage(end='', flush=True)
        view.render_stage_timing(t_spent, timing, is_passed, is_last_stage)
        if is_last_stage:
            view.render_footer()
    return total, is_passed, start_time

# stage.start
def say_stage_start(cnf, stage_number, start_number, is_restart_stage):
    if stage_number == 1 and not is_restart_stage:
        speed_ann = cnf.speech_spd
    else:
        speed_ann = cnf.start_ann_spd
    # say
    say_text(cnf.lang, 'stage', speed_ann)
    say_number(cnf.lang, stage_number, speed_ann)
    if is_restart_stage:
        say_text(cnf.lang, 'continue-with', cnf.cont_ann_spd)
        say_number(cnf.lang, start_number, cnf.cont_num_spd)
# stage.ops
def run_ops(cnf,view, stage_ops, stage_number, is_restart_stage):
    for i,op in enumerate(stage_ops):
        if not (stage_number == 1 and i == 0 and not is_restart_stage):
            time.sleep(cnf.num_delay)
        operand, number = s.split_operation(op)
        view.render_stage_op(operand, number, cnf.pls_show, end='', flush=True)
        speed_operand = cnf.pls_spd if operand == '+' else cnf.num_spd
        say_text(cnf.lang, operand, speed_operand)
        say_number(cnf.lang, number, cnf.num_spd)
# stage.deltas
def get_timing(df_run, uname, goal):
    timing = {'passed':{},'repeat':{}}
    is_passed = 1
    df = pdo.filter(df_run, where={'is_passed': is_passed}, allow_empty=True, allow_many=True)
    timing['passed']['usr'] = df2besttime(pdo.filter(df, where={'user_name': uname}, allow_empty=True, allow_many=True))
    timing['passed']['oth'] = df2besttime(pdo.filter(df, where_not={'user_name': uname}, allow_empty=True, allow_many=True))
    is_passed = 0
    df = pdo.filter(df_run, where={'is_passed': is_passed}, allow_empty=True, allow_many=True)
    timing['repeat']['usr'] = df2besttime(pdo.filter(df, where={'user_name': uname}, allow_empty=True, allow_many=True))
    timing['repeat']['oth'] = df2besttime(pdo.filter(df, where_not={'user_name': uname}, allow_empty=True, allow_many=True))
    timing['goal'] = goal
    return timing
def df2besttime(df):
    if df.empty:
        return False
    best_time_row = df.nsmallest(1, 'time')
    if best_time_row.empty:
        return False
    best_time_value = best_time_row['time'].iloc[0]
    return float(best_time_value)

# final
def add_record(df_records, uname, exercise_name, mode, is_passed, end_time):
    return pdo.addnew(df_records, {
        'rank': 0,
        'user_name': uname,
        'exercise': exercise_name,
        'is_exam': 1 if mode == 'exam' else 0,
        'is_passed': 1 if is_passed else 0,
        'time': end_time,
        'date': datetime.fromtimestamp(time.time()).strftime('%d.%m.%y')
    })
# TODO:
# TODO:
# TODO:
# TODO:
def upd_ranks(df, exercise_name):
    # df = df.sort_values(by=['is_exam', 'is_passed', 'time'], ascending=[False, False, True])
    # df['rank'] = range(1, len(df) + 1)
    # return df
    original_dtypes = df.dtypes
    df3exercise = df[df['exercise'] == exercise_name]
    df_sorted = df3exercise.sort_values(by=['is_exam', 'is_passed', 'time'], ascending=[False, False, True])
    df_sorted['rank'] = range(1, len(df_sorted) + 1)
    df.update(df_sorted)
    for column, dtype in original_dtypes.items():
        df[column] = df[column].astype(dtype)
    return df

# sounds
def prepare_fs(lang):
    cmd(f'mkdir -p ./sounds/{lang}/numbers')
def generate_sounds_texts(w, lang):
    texts = fo.yml2dict('./src/_texts4sounds.yml')
    for i,sound in enumerate(texts):
        path = f'sounds/{lang}/{sound}.mp3'
        generate_sound(lang, path, texts[sound][lang])
        progress_bar(w, 'generate speech (texts)', len(texts), i)
    print() # for progress_bar
def generate_sounds_numbers(w, lang, ops):
    for i,op in enumerate(ops):
        _, number = s.split_operation(op)
        path = f'sounds/{lang}/numbers/{number}.mp3'
        generate_sound(lang, path, num2words(number, lang=lang))
        progress_bar(w, 'generate speech (numbers)', len(ops), i)
    print() # for progress_bar
def generate_sound(lang, path, text):
    if not fo.f_exist(path):
        tts = gTTS(text=text, lang=lang)
        tts.save(path)
def progress_bar(w,msg, start_number, i):
    msg = c.ljust('>>> '+msg, 29)
    w = w - c.ln(msg) - 3 # for space and edges
    progress = int((i + 1) / start_number * w)
    done = '#' * progress
    in_progress = '.'*(w - progress)
    print(c.z(f'[x]{msg} [x][{done}{in_progress}]'), end='\r', flush=True)
def say_beep(sound, speed):
    mpv(f'sounds/{sound}.mp3', speed)
def say_text(lang, sound, speed):
    mpv(f'sounds/{lang}/{sound}.mp3', speed)
def say_number(lang, sound, speed):
    path = f'sounds/{lang}/numbers/{sound}.mp3'
    if not fo.f_exist(path):
        generate_sound(lang, path, num2words(sound, lang=lang))
    mpv(path, speed)
def mpv(path, speed):
    if not fo.f_exist(path):
        raise Exception(c.z(f'[r]ERROR:[c] MPV - File not exist: {path}'))
    if not speed:
        return False
    cmd(f'mpv {path} --speed={speed}', strict=False, verbose4fail=False)
