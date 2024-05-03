from textwrap import dedent
from pprint import pprint
# src/view
from src.view._view import View
# src/helpers
import src.helpers.colors as c

class ViewCreate(View):
    def __init__(self, w_user):
        super().__init__(w_user)
        self.legend_start = dedent('''
            [x]start-number:
              [b]S     [x]: created.
        ''').strip() + '\n'
        self.legend_roudtrip = dedent('''
            [x]roundtrip:
              [b]<     [x]: operation created.
        ''').strip() + '\n'
        self.legend_progression = dedent('''
            [x]progression:
              [b]P     [x]: operation created.
        ''').strip() + '\n'
        self.legend_cover = dedent('''
            [x]cover:
              [b]C     [x]: (y,x)  operation created.
              [y]C     [x]: (y,_)  newchain: artificially start a new chain.
              [r]C     [x]: (y,_)+ newchain: artificially increase the sum.
              [r]R     [x]: (_,_)+ random : adding a random number to increase the sum.
        ''').strip() + '\n'
        self.legend_random = dedent('''
            [x]random:
              [b]R     [x]: operation created.
              [r]e     [x]: Impossible to maintain conditions for the use of non-negative numbers.
              [x]      [x]  once change the operation to "+" and increase the range of numbers
              [y]n     [x]: Failed to maintain conditions for the use of non-negative numbers.
              [x]      [x]  once reduce the range of numbers.
              [x]99x99 [x]: new value of the numbers range.
        ''').strip() + '\n'
        self.legend = ''
        self.status = ''
    # sequence
    def upd_seq_header(self, i, kind, seq_params):
        fkind = {'p':'progression', 'r':'random', 'c':'covered'}[kind]
        self.seq_header = dedent(f'''
            [g]sequence {i+1} ({fkind}):
              [g]required: [x]{seq_params['required']}
              [g]optional: [x]{seq_params['optional']}
        ''').strip()
    # legend
    def upd_legend(self, kind):
        calls_attr = f'calls_legend_{kind}'
        legend = getattr(self, f'legend_{kind}', "")
        calls = getattr(self, calls_attr, 0)
        if calls == 0:
            self.legend += legend
            setattr(self, calls_attr, calls + 1)
    # status
    def upd_status(self, info):
        self.status += info
    def upd_status_random(self, kind, new_range):
        self.status += '{}[x]{}x{}'.format(kind, *new_range)
    def disp_status(self):
        if not self.status:
            return
        wpad = 3
        self.status = (
            self.padding(self.legend, [wpad,1,0,1]) + '\n' +
            self.padding(self.wrap(self.status, self.w - wpad*2), [wpad,0,wpad,1])
        )
        self._disp('status')

    # notes
    def upd_cover_len(self, kind, len_param, len_new_seq):
        if kind == 'less':
            self.cover_len = dedent(f'''
                [y]NOTE: cover-operation:[x] not all numbers have been generated yet for possible combinations of units.
                [y]NOTE:   [x]The specified [y]length in the parameters will be ignored.
            ''').strip()
        else:
            self.cover_len = dedent(f'''
                [y]NOTE: cover-operation:[x] all combinations were matched.
                [y]NOTE:   [x]The rest of the sequence [r]will be generated randomly.
            ''').strip()
        self.cover_len += '\n' + dedent(f'''
            [y]NOTE:   [x]the specified length in the parameters is [y]{len_param}.
            [y]NOTE:   [x]the current length is [y]{len_new_seq}.
        ''').strip()
        return True
