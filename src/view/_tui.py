import sys
import termios
import tty
import atexit
import signal

class Tui:
    def __init__(self):
        self.fd = sys.stdin.fileno()
        self.term_origin = termios.tcgetattr(self.fd)
        self.term_noecho = termios.tcgetattr(self.fd)
        self.term_noecho[3] = self.term_noecho[3] & ~termios.ECHO
        # restore
        atexit.register(self.echo)
        signal.signal(signal.SIGINT, self.signal_handler)
    # restore
    def signal_handler(self, signum, frame):
        self.echo()
        print('\nBye!')
        exit(0)

    # echo
    def noecho(self):
        self.cursor_hide()
        self.term_noecho[3] = self.term_noecho[3] & ~termios.ECHO
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.term_noecho)
    def echo(self):
        try:
            if self.fd >= 0:
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.term_origin)
                termios.tcflush(self.fd, termios.TCIFLUSH)
            self.cursor_show()
        except ValueError:
            pass
        except Exception as e:
            print("TUI - Ignored exception in echo:", e)
    def cursor_hide(self):
        sys.stdout.write('\033[?25l')
    def cursor_show(self):
        sys.stdout.write('\033[?25h')

    # cursor
    def cursor_move(self, y=None, x=None):
        if y is not None and x is not None:
            sys.stdout.write(f'\033[{y};{x}H')
        elif y is not None:
            sys.stdout.write(f'\033[{y}d')
        elif x is not None:
            sys.stdout.write(f'\033[{x}G')
        sys.stdout.flush()
    def cursor_shift(self, y=0, x=0):
        if   y > 0: sys.stdout.write(f'\033[{y}B')
        elif y < 0: sys.stdout.write(f'\033[{-y}A')
        if   x > 0: sys.stdout.write(f'\033[{x}C')
        elif x < 0: sys.stdout.write(f'\033[{-x}D')
        sys.stdout.flush()
    def cursor_save(self):
        sys.stdout.write('\033[s')
        sys.stdout.flush()
    def cursor_restore(self):
        sys.stdout.write('\033[u')
        sys.stdout.flush()

    # clear
    def clear(self, mode):
        modes = {'all': '2J', 'end': 'K', 'start': '1K', 'line': '2K', 'down': 'J', 'up': '1J'}
        char = modes.get(mode)
        if char is None:
            raise Exception(f'clear: unknown mode - {mode}')
        sys.stdout.write(f'\033[{char}')
    def clear_lines(self, count_lines):
        for _ in range(count_lines):
            sys.stdout.write('\x1b[1A')
            sys.stdout.write('\x1b[2K')
    # char
    def getch(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key
