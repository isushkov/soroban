# src/view
from src.view._view import View
from textwrap import dedent, wrap
import src.helpers.colors as c

class ViewCreate(View):
    def __init__(self):
        super().__init__()
        self.legend_cover = dedent("""
            [x]cover-operation legend:
              [b]D:[x] (y,x)  done: next pair in chain found.
              [y]N:[x] (y,_)  newchain: artificially start a new chain.
              [r]N:[x] (y,_)+ newchain: artificially increase the sum.
              [r]R:[x] (_,_)+ random: add a random number to increase the sum.
        """).strip() + '\n'
        self.legend_random = dedent("""
            [x]random-operation legend:
              [r]e[x]50x50 [y]f[x]75x75
              [r]e     [x]: Impossible to maintain conditions for the use of non-negative numbers.
              [y]n     [x]: Failed to maintain conditions for the use of non-negative numbers.
              [x]99x99 [x]: one-time new value of the numbers range.
        """).strip() + '\n'
        self.legend = ''
        self.status = ''
        self.note_cover_len = ''
    # legend/status
    def upd_status(self, info):
        if self.legend_cover:
            self.legend += self.legend_cover
            self.legend_cover = False
        self.status += info
    def upd_status_random(self, kind, new_range):
        if self.legend_random:
            self.legend += self.legend_random
            self.legend_random = False
        self.status += '{}[x]{}x{}'.format(kind, *new_range)
    def display_status(self):
        if not self.status: return
        if self.legend: c.p(self.add_padding(self.legend, [3,1,0,1]))
        status_wrapped = '\n'.join(self.wrap(c.z(self.status), 60))
        c.p(self.add_padding(status_wrapped, [3,0,0,1]))
        exit()
    # notes
    def upd_note_cover_len(self, kind, len_param, len_new_seq):
        if kind == 'less':
            self.note_cover_len = dedent(f"""
                [y]NOTE:[x] cover-operation:[c] Not all numbers have been generated yet for possible combinations of units:
                [y]NOTE:[c]   The specified [y]length in the parameters [y]will be ignored.
            """)
        else:
            self.note_cover_len = dedent(f"""
                [y]NOTE:[x] cover-operation:[c] All combinations were matched:')
                [y]NOTE:[y]   The rest of the sequence will be generated randomly.')
            """)
        self.note_cover_len += dedent(f"""
            [y]NOTE:[c]   the specified length in the parameters is {len_param}.
            [y]NOTE:[c]   the current length is [y]{len_new_seq}.
        """)
        return True
