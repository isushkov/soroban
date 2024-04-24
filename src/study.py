import time
from datetime import datetime
import pandas as pd
from src.config import Config
import src.helper as h
from src.helpers.fo import Fo as fo
from src.helpers.cmd import Cmd as cmd
from src.helpers.tui import Tui
import src.helpers.colors as c

def study(user_name_param):
    conf = Config()
    user_name = user_name_param or conf.user_name or input('Please enter your name: ').strip()[:6] or '<anon>'
    print(c.center(c.z(f' [y]STUDY PROGRAM ({self.user_name})'), 94, '=', 'x'))

    # загрузить study програм
    # найти в ней полльзователя
    # изсходя из этого
    #     найти mode
    #     найти params

    return user_name, mode, params
