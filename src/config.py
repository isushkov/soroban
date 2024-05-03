# src/helpers
from src.helpers.cmd import cmd
import src.helpers.colors as c
import src.helpers.fo as fo

class Config:
    _instance = None
    _initialized = False
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.prepare_fs()
        self.data = fo.yml2dict('config.yml')
        self.lang = self.get_lang()
        self.uname = self.get_uname()
        self.w = self.set_int('common.view_width', allow_zero=True, default=80)
        self.spoilers = self.set_bool('common.analyze_spoilers', default=False)
        self.t2e = self.set_int('common.study_program.passes_for_exam', default=3)
        self.e2t = self.set_int('common.study_program.fails_for_retake', default=0, allow_zero=True)
    def init4mode(self, mode):
        # exam/training
        sfx = f'{mode}.non_exercise'
        self.speech_spd = self.set_percent(f'{sfx}.speech_spdpct', default=100)
        self.signals_spd = self.set_percent(f'{sfx}.signals_spdpct', default=100)
        sfx = f'{mode}.during_exercise'
        self.num_spd = self.set_percent(f'{sfx}.number_spdpct', default=100)
        self.num_delay = self.set_ms(f'{sfx}.number_delay_ms', default=3000)
        self.pls_show = self.set_bool(f'{sfx}.unaryplus_show', default=True)
        self.pls_spd = self.set_percent(f'{sfx}.unaryplus_spdpct', default=0)
        self.res_entry_spd = self.set_percent(f'{sfx}.result_entry_spdpct', default=100)
        # training
        sfx = f'training.during_exercise'
        self.num_per_stage = self.set_int('training.numbers_per_stage', default=10)
        self.check_method = self.get_check_method()
        self.start_ann_spd = self.set_percent(f'{sfx}.startstage_announce_spdpct', 100)
        self.start_sig_spd = self.set_percent(f'{sfx}.startstage_signal_spdpct', 100)
        self.cont_ann_spd = self.set_percent(f'{sfx}.continuewith_announce_spdpct', 100)
        self.cont_num_spd = self.set_percent(f'{sfx}.continuewith_number_spdpct', 100)
        self.res_ann_spd = self.set_percent(f'{sfx}.result_announce_spdpct', 100)
        self.res_num_spd = self.set_percent(f'{sfx}.result_number_spdpct', 100)
        self.res_wrong_spd = self.set_percent(f'{sfx}.result_wrong_spdpct', 100)
    # fs
    def prepare_fs(self):
        if not fo.f_exist('config.yml'):
            cmd('copy ./examples/config.yml ./config.yml')
    # common
    def e404(self, path, default):
        c.p(f'[y]CONFIG ERROR:[x] Config value [c]not found:')
        c.p(f'[y]CONFIG ERROR:[x]   [r].{path}')
        c.p(f'[y]CONFIG ERROR:[x]   Was replaced by [y]{default}')
        return default
    def e400(self, path, val, default):
        c.p(f'[y]CONFIG ERROR:[x] Config value is [c]invalid:')
        c.p(f'[y]CONFIG ERROR:[x]   .{path}: [r]{val}[c]')
        c.p(f'[y]CONFIG ERROR:[x]   Was replaced by [y]{default}')
        return default
    def find(self, path, default, skip_errors=False):
        value = self.data
        for key in path.split('.'):
            if not key in value:
                value = default if skip_errors else self.e404(path, default)
            value = value[key]
        return value
    # sets
    def set_percent(self, path, default):
        val = int(self.find(path, default))
        if val == 0:
            return False
        if not (50 <= val <= 500):
            val = self.e400(path, val, default)
        return val / 100
    def set_ms(self, path, default):
        val = int(self.find(path, default))
        if val < 0:
            val = self.e400(path, val, default)
        return int(val / 1000)
    def set_int(self, path, default=1, allow_zero=False, allow_negative=False):
        val = int(self.find(path, default))
        if not allow_negative and val <  0: val = self.e400(path, val, default)
        if not allow_zero     and val == 1: val = self.e400(path, val, default)
        return val
    def set_bool(self, path, default):
        val = self.find(path, default)
        if not isinstance(val, bool):
            val = self.e400(path, val, default)
        return val
    # gets
    def get_lang(self, path='common.lang', default='en'):
        val = self.find(path, default)
        if len(val) != 2:
            val = self.e400(path, val, default)
        if val not in ['en', 'ru']:
            c.p(f'[y]NOTE: [x]the language [y]"{val}"[c] has not been tested.')
            c.p(f'[y]NOTE: [x]the language will be generated automatically - it may be ugly :(')
        return val
    def get_uname(self, path='common.user_name', default=False):
        val = self.find(path, default, skip_errors=True)
        return val.strip()[:6] if val else default
    def get_check_method(self, path='training.check_result_method', default='input'):
        val = self.find(path, default, skip_errors=True)
        if val not in ['input', 'yes-no']:
            val = self.e400(path, val, default)
        return val
