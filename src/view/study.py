from textwrap import dedent
import re
# src/view
from src.view._view import View
# src/helpers
import src.helpers.colors as c

class ViewStudy(View):
    def __init__(self, w_sttgs):
        super().__init__(w_sttgs)
        # uname
        self.uname_note = dedent('''
            [y]NOTE: [x]You can specify a temporary username using the optional argument [b]--user-name=[x]<user-name>
            [y]NOTE: [x]or set a permanent one in [b]config.yml [x](--user-name has a higher priority):
            [y]NOTE: [x]    [b].common.user_name:[c] <user-name> [x]# 1-6 chars
        ''').strip()
        self.uname_err = '[c]The user-name [r]is required[c] for [b]the study-mode[c].'
        # idstep/idmode
        self.idstep_start = '[b]>>> INFO: [x]Identifying [b]the STUDY-STEP..'
        self.idstep_unknown = dedent('''
            [b]EXIT: [x]Study-step not identified:
            [b]EXIT:   [g]You've already passed everything?
        ''').strip()
        self.idmode_start = '[b]>>> INFO: [x]Identifying [b]the MODE [x]for study-step..'

    # idstep
    def upd_idstep_passed(self, step, params):
        self.idstep_passed = f'[b]>>> INFO: [x]Step {step}: [g]passed [x]({params}).'
    def upd_idstep_not_found(self, step, params):
        self.idstep_not_found = f'[b]>>> INFO: [x]records not found.\n'
        self.idstep_not_found += self.dec_idstep_done(step, params)
    def upd_idstep_not_passed(self, step, params):
        self.idstep_not_passed = f'[b]>>> INFO: [x]Step {step}: [y]not passed [x]({params}).\n'
        self.idstep_not_passed += self.dec_idstep_done(step, params)
    def dec_idstep_done(self, step, params):
        return f'[g]>>> INFO: [x]Current [g]step is {step} [x]({params}).'
    # idmode
    def upd_idmode_training(self, code):
        w_time = f'[y]within the specified time'
        pfx = '[x]for this exercise'
        code2msg = {
            '404': f'[b]>>> INFO: [x]So far, no trainings have been passed {pfx}.',
            '422': f'[b]>>> INFO: [x]So far, no trainings have been passed {w_time} {pfx}.',
            't2e': f'[b]>>> INFO: [x]The training was [y]completed fewer times [x]in a row than necessary {pfx}.',
            'e2t': f'[b]>>> INFO: [x]The exam is [r]retaken more times in a row [x]than possible {pfx}.'
        }
        self.idmode_training = code2msg[code] + '\n'
        self.idmode_training += self.dec_idmode_done('y', 'training')
    def upd_idmode_exam(self):
        self.idmode_exam = '[g]>>> INFO: Admission to the exam has been received.\n'
        self.idmode_exam += self.dec_idmode_done('r', 'exam')
    def dec_idmode_done(self, color, mode):
        return f'[b]>>> INFO:[x] Current mode is [{color}]{mode.upper()}[x].'

    # status
    def upd_status(self, uname, step, mode, goal, params, trainings_passed, exams_failed, t2e, e2t, comment):
        color = 'r' if mode == 'exam' else 'y'
        self.status = self.padding(dedent(f'''
            [x]{comment}

            [x]{c.ljust(uname+':',7)}           [g]Step-{step}.[{color}]{mode.upper()}
            [x]Exercise:         [b]{params}
            [x]Goal time:        [r]{self.dec_colorize_ft(goal, v_color='y', z_color='x')}
            [x]Trainings passed: [{'g' if trainings_passed else 'x'}]{trainings_passed}[x]/{t2e}
            [x]Exam retakes:     [{'r' if exams_failed else 'x'}]{exams_failed}[x]/{e2t}
        ''').strip(), [3,1,0,1])

    def dec_colorize_ft(self, ft, v_color, z_color):
        v_color, z_color = '['+v_color+']', '['+z_color+']'
        match = re.search('[1-9]\d*', ft)
        if match:
            zeros = ft[:match.start()]
            values = ft[match.start():]
            ft = z_color + zeros + v_color + values
        else:
            ft = v_color + ft
        return ft
