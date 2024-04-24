import time
from datetime import datetime
import pandas as pd
from src.config import Config
import src.helper as h
from src.helpers.fo import Fo as fo
from src.helpers.cmd import Cmd as cmd
from src.helpers.tui import Tui
import src.helpers.colors as c

def study(arg_user_name):
    # args/conf/fs
    conf = Config()
    user_name = arg_user_name or conf.user_name or input('Please enter your name: ').strip()[:6] or '<anon>'
    csv_columns = ['id','user_name','step','t2e','e2t']
    prepare_fs(csv_columns)
    print(c.center(c.z(f' [y]STUDY PROGRAM ({user_name})'), 94, '=', 'x'))

    # загрузить study програм
    # найти в ней полльзователя
    # изсходя из этого
    #     найти mode
    #     найти params
    # path = create(path=False, params=params)
    # analyze(path)
    # Run(path, mode, user_name)
    # save id,user_name,step,t2e,e2f

def prepare_fs(csv_columns):
    if not fo.f_exist('./src/__study.csv'):
        cmd.run(f"echo {','.join(csv_columns)} > ./src/__study.csv")
