from textwrap import dedent
# src/view
from src.view._view import View
# src/helpers
import src.helpers.colors as c

class ViewStudy(View):
    def __init__(self):
        super().__init__()
        # uname
        self.uname_note = dedent('''
            [y]NOTE:[x] You can specify a temporary username using the optional argument [b]--user-name=[x]<user-name>
            [y]NOTE:[x] or set a permanent one in [b]config.yml[c] (--user-name has a higher priority)[x]:
            [y]NOTE:[x]     [b].common.user_name:[c] <user-name> [x]# 1-6 chars
        ''').strip()
        self.uname_err = '[r]EXIT:[c] The user-name [r]is required[y] for the study-mode.'
        # idstep
        self.idstep_start = '[b]INFO: >>>[x] Identifying the STUDY-STEP..'
        self.idstep_unknown = dedent('''
            [b]INFO:[x] Study-step not identified:
            [b]INFO:[g]   You've already passed everything?
        ''').strip()
    # idstep
    def upd_idstep_404(self, step, exercise):
        self.idstep_404 = dedent(f'''
            [b]INFO:[c] records not found.
            [b]INFO:[c] Current step is {step} ({exercise}).
        ''').strip()
    def upd_idstep_passed(self, step, exercise):
        self.idstep_passed = f'[b]INFO:[x] Step {step}:[g] passed [x]({exercise}).'
    def upd_idstep_found(self, step, exercise):
        self.idstep_found = f'[g]INFO:[x] Current step is [g]{step} [x]({exercise}).'
    # idmode
    def upd_idmode_start(self):
        self.idmode_start = '[b]INFO: >>>[x] Identifying [b]the MODE for study-step..')
    def upd_idmode_training(self, code):
        w_time = f'[c]within the specified time'
        pfx = '[x]for this exercise'
        code2msg = {
            '404': f'[x]INFO: [x]So far, no trainings have been passed {pfx}.',
            '422': f'[x]INFO: [x]So far, no trainings have been passed {w_time} {pfx}.'
            't2e': f'[y]INFO: [x]The training was [y]completed fewer times [x]in a row than necessary {pfx}.')
            'e2t': f'[r]INFO: [x]The exam is [r]failed more times in a row than possible {pfx}.')
        }
        self.idmode_training = code2msg[code]
        self.idmode_training += self.dec_idmode_done('y', 'training')
    def upd_idmode_exam(self):
        self.idmode_exam = '[g]INFO: Admission to the exam has been received.')
        self.idmode_exam += self.dec_idmode_done('r', 'exam')
    def dec_idmode_done(self, color, mode):
        return f'[{color}]INFO:[x] Current mode [{color}]is "{mode.upper()}"[x].'

    # ready
    def upd_ready(self, uname, step, mode, target, params, trainings_passed, exams_failed, conf):
        color = 'r' if mode == 'exam' else 'y'
        self.ready = dedent(f'''
            [y]>>>> {uname}:
            [b]>>>> Step {step}: [{color}]{mode.upper()}. [x]target-time: [r]{target}[x]. exercise: '{params}'
            [x]>>>>   trainings-passed: [c]{trainings_passed}[g]/{conf.t2e}[c]
            [x]>>>>   exams-failed:     [c]{exams_failed}[r]/{conf.e2t}
        ''').strip()
