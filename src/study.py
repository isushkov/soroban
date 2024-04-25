import time
import pandas as pd
from datetime import datetime
from src.config import Config
from src.params import parse_params, params2basename
from src.helpers.fo import Fo as fo
from src.helpers.cmd import Cmd as cmd
import src.helper as h
import src.helpers.colors as c

def study(arg_style, arg_user_name):
    # args/conf/fs
    if arg_style != 'abacus':
        h.todo(f'study, style: {style}')
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
    print(c.center(c.z(f' [y]STUDY PROGRAM ({user_name})'), 94, '=', 'x'))
    # load data
    data_records = csv.get_df('./src/__records.csv')
    data_study_program = csv.get_df('./src/__study_program.yml')
    data_study_users = csv.get_df('./src/__study_users.yml')
    print(data_records)
    print(data_study_program)
    print(data_study_users)
    exit()
    # -------------------------------------------------------------------------

    # step/create/analyze
    step, target, params_str, exercise = find_step_data(user_name, data_records, data_study_program)
    path = create(path=False, params=params_str)
    analyze(path)
    # mode
    trainings_passed, exams_failed = data_study_users[user_name] # TODO
    mode = find_mode(data_records, user_name, exercise, target,
                     trainings_passed, exams_failed, conf.t2e, conf.e2t)
    # run
    # show main info.. # TODO
    # show config.. # TODO
    # press enter to continue.. #TODO
    # TODO: обработчик если начато но не закончено - априори записать плохой результат
    is_passed, end_time = Run(path, mode, user_name, target)

    # TODO: result
    # if not is_passed:
    #     result = False
    # if is_passed:
    #     сравнить end_time и target

    # TODO: show results

    # save
    # save study_users # TODO
    if mode == training:
        exams_failed = 0
        if result:
            trainings_passed += 1
        else:
            trainings_passed = 0
    if mode == exam:
        trainings_passed = 0
        if result:
            exams_failed = 0
        else:
            exams_failed += 1

def prepare_fs():
    study_users_columns = ['id','user_name','step','trainings_passed','exams_failed']
    if not fo.f_exist('./src/__study_users.csv'):
        cmd.run(f"echo {','.join(study_users_columns)} > ./src/__study_users.csv")
    f = './src/__study_program.csv'
    if not fo.f_exist(f):
        raise FileNotFoundError(c.z(f'[r]ERROR:[c] file not found {f}'))
def find_step_data(user_name, data_records, data_study_program):
    c.p(f'[b]INFO: >>>[c] Identifying the STUDY-STEP..')
    # TODO
    for step, target, params_str in enumerate(data_study_program.items()):
        exercise = params2basename(parse_params(params_str))
        # TODO
        if not (data_records: name=user_name, exercise=exercise,
                              is_exam=1, is_passed=1 and time <= target):
            c.p(f'[g]INFO:[c] current step is {step} ({exercise}).')
            return step, target, params_str, exercise
        c.p(f'[b]INFO: step {step}[c] - passed ({exercise}).')
    c.p(f'[y]NOTE:[c] Study-step not identified:')
    c.p(f'[y]NOTE:[c] [g]You\'ve already passed everything?')
    exit(0)
def find_mode(data_records, user_name, exercise, target,
              trainings_passed, exams_failed, conf.t2e, conf.e2t):
    c.p(f'[b]INFO: >>>[c] Identifying the MODE for study-step..')
    # TODO
    if not (data_record: name=user_name, exercise=exercise, is_exam=0, is_passed=1):
        c.p(f'[b]INFO:[c] So far, no trainings have been passed.')
        c.p('[b]INFO:[c] Current mode is [y]"training".')
        return 'training'
    # TODO
    if not (data_record: name=user_name, exercise=exercise, is_exam=0, is_passed=1 and time <= target):
        c.p(f'[b]INFO:[c] So far, no exams have been passed within the specified time ({target}).')
        c.p('[b]INFO:[c] Current mode is [y]"training".')
        return 'training'
    if trainings_passed < t2e:
        c.p(f'[y]INFO:[c] The training was completed fewer times in a row than necessary within the specified time ({target}).')
        c.p('[y]INFO:[c] Current mode is [y]"training".')
        return 'training'
    if exams_failed > e2t:
        c.p(f'[r]INFO:[c] The exam is failed more times in a row than possible within the specified time ({target}).')
        c.p('[r]INFO:[c] Current mode is [y]"training".')
        return 'training'
    c.p('[g]INFO:[c] Admission to the exam has been received.')
    c.p('[g]INFO:[c] Current mode is [r]"exam".')
    return 'exam'
