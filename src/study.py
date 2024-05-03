import time
import re
from datetime import datetime
# src
from src.config import Config
from src.params import parse_params, params2basename
from src.create import create
from src.analyze import analyze
from src.run import run
import src.sequence as s
# src/view
from src.view.study import ViewStudy
# src/helpers
from src.helpers.cmd import cmd
import src.helpers.fo as fo
import src.helpers.pdo as pdo
import src.helpers.colors as c

cfg = Config()
view = ViewStudy(cfg.w)
def study(arg_uname):
    view.render_title(f'[y]STUDY PROGRAM', char='_')
    # args/cfg/fs
    prepare_fs()
    uname = arg_uname or cfg.uname
    if not uname:
        view.disp_uname_note()
        uname = input('Please enter your name: ').strip()[:6]
        if not uname:
            view.disp_uname_err()
    # load/filter data
    study_attempts_columns = ['id','user_name','step','trainings_passed','exams_failed']
    df_study_attempts = pdo.load('./src/__study_attempts.csv', study_attempts_columns)
    df_records = pdo.load('./src/__records.csv', allow_empty=True)
    df_study_attempts4user = pdo.filter(df_study_attempts, where={'user_name': uname }, allow_empty=True)
    df_records4user = pdo.filter(df_records, where={'user_name': uname }, allow_empty=True, allow_many=True)
    data_study_program = get_study_program()
    # create/analyze
    step, target, params, exercise = idstep(df_records4user, data_study_program)
    view.render_sepline('>')
    path = create(path=False, params=params)
    analyze(path)
    view.render_sepline('<')
    # mode
    trainings_passed, exams_failed = get_attempts(df_study_attempts)
    mode = idmode(df_records4user, uname, exercise, target, trainings_passed, exams_failed, cfg.t2e, cfg.e2t)
    # interrupt-handler/run
    view.render_status(uname, step, mode, target, params, trainings_passed, exams_failed, cfg)
    interrupt_handler(df_study_attempts, uname, mode, trainings_passed, exams_failed)
    is_passed, time_seconds = run(path, mode, uname, target)
    # result/save
    result = get_result(is_passed, time_seconds, target)
    trainings_passed, exams_failed = upd_attempts(mode, result, trainings_passed, exams_failed)
    save_study_attempts(df_study_attempts, uname, trainings_passed, exams_failed)

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
def save_study_attempts(df_study_attempts, uname, trainings_passed, exams_failed):
    values = {'trainings_passed':str(trainings_passed), 'exams_failed':str(exams_failed)}
    df = pdo.update(df_study_attempts, where={'user_name':uname}, values=values, allow_addnew=True, allow_many=False)
    pdo.save(df, './src/__study_attempts.csv')
def interrupt_handler(df_study_attempts, uname, mode, trainings_passed, exams_failed):
    trainings_passed, exams_failed = upd_attempts(mode, False, trainings_passed, exams_failed)
    save_study_attempts(df_study_attempts, uname, trainings_passed, exams_failed)
# idstep
def idstep(df_records4user, data_study_program):
    view.disp_idstep_start()
    if df_records4user.empty:
        step = 0
        target, params = data_study_program[step]
        exercise = params2basename(parse_params(params))
        view.render_idstep_not_found(step, params)
        return step, target, params, exercise
    for step, [target, params] in enumerate(data_study_program):
        exercise = params2basename(parse_params(params))
        where = {'exercise':exercise,'is_exam':1,'is_passed':1}
        df_passed_exams = pdo.filter(df_records4user, where=where, allow_empty=True, allow_many=True)
        if df_passed_exams[df_passed_exams['time_seconds'] <= target2seconds(target)].empty:
            view.render_idstep_not_passed(step, params)
            return step, target, params, exercise
        view.render_idstep_passed(step, params)
    view.disp_idstep_unknown()
    exit(0)
# idmode
def idmode(df_records4user, uname, exercise, target, trainings_passed, exams_failed, t2e, e2t):
    mode = 'training'
    where = {'exercise':exercise,'is_exam':0,'is_passed':1}
    df_passed_trainings = pdo.filter(df_records4user, where=where, allow_empty=True, allow_many=True)
    view.disp_idmode_start()
    if df_passed_trainings.empty:
        view.render_idmode_training('404')
        return mode
    if df_passed_trainings[df_passed_trainings['time_seconds'] <= target2seconds(target)].empty:
        view.render_idmode_training('422')
        return mode
    if trainings_passed < t2e:
        view.render_idmode_training('t2e')
        return mode
    if exams_failed > e2t:
        view.render_idmode_training('e2t')
        return mode
    view.render_idmode_exam()
    return 'exam'
