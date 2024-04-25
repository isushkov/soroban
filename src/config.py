from src.helpers.fo import Fo as fo
import src.helpers.colors as c
from src.helpers.fo import Fo as fo
from src.helpers.cmd import Cmd as cmd

class Config:
    def __init__(self):
        # args/fs
        self.prepare_fs()
        self.data = fo.yml2dict('config.yml')
        # common
        self.lang = self.get_lang()
        self.mode = mode if mode else self.get_mode()
        self.user_name = self.get_user_name()
        self.t2e = self.get_study_switch('training2exam')
        self.e2t = self.get_study_switch('exam2training')
        # shared
        self.spd_speech = self.get_percent(self.mode, 'out', 'speech_percents')
        self.spd_signals = self.get_percent(self.mode, 'out', 'signals_percents')
        self.show_plus = self.get_yesno(self.mode, 'in', 'show_unary_plus')
        self.spd_plus = self.get_percent(self.mode, 'in', 'announce_unary_plus_percents')
        self.spd_number = self.get_percent(self.mode, 'in', 'announce_number_percents')
        self.spd_delay = self.get_delay(self.mode)
        enter_result_key = 'announce_enter_answer_percents' if self.mode == 'exam' else 'announce_enter_stage_result_percents'
        self.spd_enter_result = self.get_percent(self.mode, 'in', enter_result_key)
        # training
        self.numbers_per_stage = self.get_number_per_stage()
        self.check_method = self.get_check_method()
        self.spd_stage = self.get_percent('training', 'in', 'announce_stage_percents')
        self.spd_stage_cont_txt = self.get_percent('training', 'in', 'announce_stage_continue_with_text_percents')
        self.spd_stage_cont_num = self.get_percent('training', 'in', 'announce_stage_continue_with_number_percents')
        self.spd_start = self.get_percent('training', 'in', 'signal_start_stage_percents')
        self.spd_result_txt = self.get_percent('training', 'in', 'announce_stage_result_text_percents')
        self.spd_result_num = self.get_percent('training', 'in', 'announce_stage_result_number_percents')
        self.spd_wrong = self.get_percent('training', 'in', 'signal_wrong_stage_result_percents')

    # args/fs
    def prepare_fs():
        if not fo.f_exist('config.yml'):
            cmd.run('copy ./examples/config.yml ./config.yml')
    # common
    if not fo.f_exist('./src/__study.csv'):
        cmd.run(f'echo {",".join(self.records_columns)} > ./src/__study.csv')
    def config_error(self, key, val, replacement):
        c.p(f'[y]CONFIG ERROR:[c] Invalid config value [r]"{key}: {val}"')
        c.p(f'[y]CONFIG ERROR:[c] Was replaced by [g]"{replacement}"')
        return replacement
    def get_percent(self, mode, direction, key):
        direction = 'throughout_the_exercise' if direction == 'in' else 'outside_the_exercise'
        val = int(self.data[mode]['speed'][direction][key])
        if val == 0:
            return False
        if not (50 <= val <= 500):
            return self.config_error(f'.{mode}.{direction}.{key}', val, 100) / 100
        return val / 100
    def get_delay(self, mode):
        val = int(self.data[mode]['speed']['throughout_the_exercise']['delay_between_numbers_ms'])
        if val < 0:
            return self.config_error(f'.{mode}.throughout_the_exercise.delay_between_numbers_ms', val, 3)
        return val / 1000

    # specific
    def get_lang(self):
        val = self.data['common']['lang']
        if len(val) != 2:
            return self.config_error('.common.lang', val, 'en')
        if val not in ['en', 'ru']:
            c.p('[y]NOTE:[c] Lang [y]{val}[c] Will be generated automatically. May be ugly or not working at all.')
        return val
    def get_mode(self):
        val = self.data['common']['mode']
        if val not in ['exam', 'training']:
            return self.config_error('.common.mode', val, 'training')
        return val
    def get_user_name(self):
        user_name = self.data['common'].get('user_name')
        return user_name.strip()[:6] if user_name else False
    def self.get_study_switch(self, kind):
        key, default = ('training2exam', 1) if kind == 'training2exam' else ('exam2training', 3)
        switch = self.data['common']['study_program']['switch_mode_policy'][key]
        if switch <= 1:
            return self.config_error(f'.common.study_program.switch_mode_policy.{key}', switch, default)
        return switch
    def get_yesno(self, mode, direction, key):
        direction = 'throughout_the_exercise' if direction == 'in' else 'outside_the_exercise'
        val = int(self.data[mode]['speed'][direction][key])
        if val == 'yes': return True
        if val == 'no':  return False
        return self.config_error(f'.{mode}.{direction}.{key}', val, 'yes')
    def get_number_per_stage(self):
        val = int(self.data['training']['max_count_numbers_per_stage'])
        if val <= 0:
            return self.config_error('.training.max_count_numbers_per_stage', val, 10)
        return val
    def get_check_method(self):
        val = self.data['training']['check_stage_result_method']
        if val not in ['input', 'yes-no']:
            return self.config_error('.training.check_stage_result_method', val, 'yes-no')
        return val
