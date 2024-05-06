import curses
import sys
from src.helpers import colors as c


class CursesInterface:
    # init/end без очистки экрана
    def __init__(self):
        self.stdscr = curses.initscr()
        curses.cbreak() # обработка нажатий
        self.stdscr.keypad(True) # специальные клавиши
        self.stdscr.scrollok(True) # прокрутка экрана
        self.echo() # echo by_default
    def end(self):
        self.stdscr.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    # echo
    def echo(self):
        curses.echo()
        curses.curs_set(1)
    def noecho(self):
        curses.noecho()
        curses.curs_set(0)

    # cursor
    def show(self): curses.curs_set(1)
    def hide(self): curses.curs_set(0)
    def getyx(self): return self.stdscr.getyx()
    def move(self, y=None, x=None):
        cy, cx = self.stdscr.getyx()
        if y is None: y = cy
        if x is None: x = cx
        self.stdscr.move(y, x)
        self.stdscr.refresh()
    def shift(self, y=None, x=None):
        cy, cx = self.stdscr.getyx()
        if y is None: y = cy + y
        if x is None: x = cx + x
        self.stdscr.move(cy + y, cx + x)
        self.stdscr.refresh()

    # clear
    def clear_lines(self, count_lines):
        cy, cx = self.stdscr.getyx()
        for _ in range(count_lines):
            self.shift(-1,0)
            self.stdscr.deleteln()
        self.stdscr.refresh()
    def clear(self, mode):
        modes = {
            'all': self.stdscr.clear,
            'end': self.stdscr.clrtoeol,
            'start': lambda: (self.stdscr.move(self.stdscr.getyx()[0], 0), self.stdscr.clrtobot()),
            'line': self.stdscr.deleteln,
            'down': self.stdscr.clrtobot,
            'up': self.stdscr.clrtoeol,
        }
        action = modes.get(mode)
        if action:
            action()
        else:
            raise Exception(f'clear: unknown mode - {mode}')
        self.stdscr.refresh()

    # input/menus
    def getch(self):
        return self.stdscr.getch()
    def menu_yesno(self):
        key = self.getch()
        return key in [curses.KEY_ENTER, ord(' '), ord('\n')]
    def menu_input(self):
        self.echo()
        answer = self.stdscr.getstr().decode()
        self.noecho()
        return answer
