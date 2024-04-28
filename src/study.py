import time
import re
import pandas as pd
from datetime import datetime
from src.config import Config
from src.params import parse_params, params2basename
from src.create import create
from src.analyze import analyze
from src.run import run
import src.sequence as s
import src.helpers.fo as fo
import src.helpers.pdo as pdo
import src.helpers.colors as c
from src.helpers.cmd import cmd

def study(arg_user_name):
    # args/conf/fs
    prepare_fs()
    conf = Config()
    user_name = arg_user_name or conf.user_name
    if not user_name:
        c.p(f'[y]NOTE:[c] You can specify a temporary username using the optional argument [y]--user-name=<user-name>')
        c.p(f'[y]NOTE:[c] or set a permanent one in [g]config.yml[c] (--user-name has a higher priority):')
        c.p(f'[y]NOTE:[c]     [g].common.user_name:[c] <user-name> [x]# 1-6 chars')
        user_name = input('Please enter your name: ').strip()[:6]
        if not user_name:
            c.p(f'[r]EXIT:[c] The user-name [r]is required[y] for the study-mode.')
    print(c.center(c.z(f' [y]STUDY PROGRAM  for {user_name} '), 94, '>', 'x'))
    # load/filter data
    study_attempts_columns = ['id','user_name','step','trainings_passed','exams_failed']
    df_study_attempts = pdo.load('./src/__study_attempts.csv', study_attempts_columns)
    df_records = pdo.load('./src/__records.csv', empty_allowed=True)
    df_study_attempts4user = pdo.filter(df_study_attempts, where={'user_name': user_name }, empty_allowed=True)
    df_records4user = pdo.filter(df_records, where={'user_name': user_name }, empty_allowed=True, many_allowed=True)
    data_study_program = get_study_program()
    # step/create/analyze
    step, target, params, exercise = identify_step(df_records4user, data_study_program)
    path = create(path=False, params=params)
    analyze(path)
    # mode
    trainings_passed, exams_failed = get_attempts(df_study_attempts)
    mode = identify_mode(df_records4user, user_name, exercise, target, trainings_passed, exams_failed, conf.t2e, conf.e2t)
    # get-ready
    color = 'r' if mode == 'exam' else 'y'
    c.p(f'[x]>>> [y]{user_name}[x], get ready:')
    c.p(f'[b]>>> Step {step}: [{color}]{mode.upper()}. [x]target-time: [r]{target}[x]. exercise: "{params}"')
    c.p(f'[x]>>> trainings-passed: [c]{trainings_passed}[g]/{conf.t2e}[c]')
    c.p(f'[x]>>> exams-failed:     [c]{exams_failed}[r]/{conf.e2t}')
    input('Press Enter to continue...')
    # interrupt-handler/run
    interrupt_handler(df_study_attempts, user_name, mode, trainings_passed, exams_failed)
    is_passed, time_seconds = run(path, mode, user_name, target)
    # result/save
    result = get_result(is_passed, time_seconds, target)
    trainings_passed, exams_failed = upd_attempts(mode, result, trainings_passed, exams_failed)
    save_study_attempts(df_study_attempts, user_name, trainings_passed, exams_failed)

# common/attempts/result
def prepare_fs():
    f = './src/__study_program.txt'
    if not fo.f_exist(f):
        raise FileNotFoundError(c.z(f'[r]ERROR:[c] file not found - {f}'))
def get_study_program():
    study_program = []
    for line in fo.txt2str('./src/__study_program.txt').splitlines():
        line = line.strip()
        if not line: continue
        if not line[0].isdigit(): continue
        parts = line.split(':')
        data = [parts[0].strip(), re.sub(r'\s+', ' ', ':'.join(parts[1:]).strip())]
        study_program.append(data)
    return study_program
def target2seconds(target):
    minutes, seconds = map(float, target.split('.'))
    seconds = minutes * 60 + seconds
    return seconds
def get_attempts(df_study_attempts4user):
    if df_study_attempts4user.empty:
        return (0, 0)
    trainings_passed = df_study_attempts4user.iloc[0, 1]
    exams_failed = df_study_attempts4user.iloc[0, 2]
    return (trainings_passed, exams_failed)
def upd_attempts(mode, result, trainings_passed, exams_failed):
    if mode == 'training':
        return (trainings_passed+1, 0) if result else (0, 0)
    return (0, 0) if result else (exams_failed+1, 0)
def get_result(is_passed, time_seconds, target):
    if not is_passed:
        return False
    if time_seconds <= target2seconds(target):
        return True
    return False
def save_study_attempts(df_study_attempts, user_name, trainings_passed, exams_failed):
    values = {'trainings_passed':str(trainings_passed), 'exams_failed':str(exams_failed)}
    df = pdo.update(df_study_attempts, where={'user_name':user_name}, values=values, addnew_allowed=True, many_allowed=False)
    pdo.save(df, './src/__study_attempts.csv')
def interrupt_handler(df_study_attempts, user_name, mode, trainings_passed, exams_failed):
    trainings_passed, exams_failed = upd_attempts(mode, False, trainings_passed, exams_failed)
    save_study_attempts(df_study_attempts, user_name, trainings_passed, exams_failed)
# inentify
def identify_step(df_records4user, data_study_program):
    c.p(f'[b]INFO: >>>[c] Identifying the STUDY-STEP..')
    if df_records4user.empty:
        step = 0
        target, params = data_study_program[step]
        exercise = params2basename(parse_params(params))
        c.p(f'[b]INFO:[c] records not found.')
        c.p(f'[b]INFO:[c] Current step is {step} ({exercise}).')
        return step, target, params, exercise
    for step, [target, params] in enumerate(data_study_program):
        exercise = params2basename(parse_params(params))
        where = {'exercise':exercise,'is_exam':1,'is_passed':1}
        df_passed_exams = pdo.filter(df_records4user, where=where, empty_allowed=True, many_allowed=True)
        if df_passed_exams[df_passed_exams['time_seconds'] <= target2seconds(target)].empty:
            c.p(f'[g]INFO:[c] Current step is {step} ({exercise}).')
            return step, target, params, exercise
        c.p(f'[b]INFO: Step {step}[c] - passed ({exercise}).')
    c.p(f'[y]NOTE:[c] Study-step not identified:')
    c.p(f'[y]NOTE:[c] [g]You\'ve already passed everything?')
    exit(0)
def identify_mode(df_records4user, user_name, exercise, target, trainings_passed, exams_failed, t2e, e2t):
    c.p(f'[b]INFO: >>>[c] Identifying the MODE for study-step..')
    mode, sfx_time = 'training', f'within the specified time ({target}).'
    where = {'exercise':exercise,'is_exam':0,'is_passed':1}
    df_passed_trainings = pdo.filter(df_records4user, where=where, empty_allowed=True, many_allowed=True)
    if df_passed_trainings.empty:
        c.p(f'[b]INFO:[c] So far, no trainings have been passed.')
        return info_mode(mode)
    if df_passed_trainings[df_passed_trainings['time_seconds'] <= target2seconds(target)].empty:
        c.p(f'[b]INFO:[c] So far, no training have been passed {sfx_time}.')
        return info_mode(mode)
    if trainings_passed < t2e:
        c.p(f'[y]INFO:[c] The training was completed fewer times in a row than necessary {sfx_time}')
        return info_mode(mode)
    if exams_failed > e2t:
        c.p(f'[r]INFO:[c] The exam is failed more times in a row than possible {sfx_time}')
        return info_mode(mode)
    c.p('[g]INFO: Admission to the exam has been received.')
    return info_mode('exam')
def info_mode(mode):
    color = 'r' if mode == 'exam' else 'y'
    c.p(f'[g]INFO:[c] Current mode is [{color}]"{mode}".')
    return mode
