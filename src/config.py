from src.helpers.fo import Fo as fo
from src.helpers.colors import *

class Config:
    def __init__(self):
        self.data = fo.yml2dict('config.yml')
        # common
        self.lang = self.get_lang()
        self.mode = self.get_mode()
        self.course_of_study_step = self.data['common']['course_of_study_step'] # TODO
        # shared
        self.spd_speech = self.get_percent(self.mode, 'out', 'speech_percents')
        self.spd_signals = self.get_percent(self.mode, 'out', 'signals_percents')
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

    # config
    def config_error(self, key, val, replacement):
        print(cz(f'[y]CONFIG ERROR:[c] Invalid config value [r]"{key}: {val}"'))
        print(cz(f'[y]CONFIG ERROR:[c] Was replaced by [g]"{replacement}"'))
        return replacement
    def get_lang(self):
        val = self.data['common']['lang']
        if len(val) != 2:
            return self.config_error('.common.lang', val, 'en')
        if val not in ['en', 'ru']:
            print(cz('[y]NOTE:[c] Lang [y]{val}[c] Will be generated automatically. May be ugly or not working at all.'))
        return val
    def get_mode(self):
        val = self.data['common']['mode']
        if val not in ['exam', 'training']:
            return self.config_error('.common.mode', val, 'training')
        return val
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
