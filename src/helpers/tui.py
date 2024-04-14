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
        print("\nTUI-Signal handler..")
        exit(0)

    # echo
    def noecho(self):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.term_noecho)
        self.cursor_hide()
    def echo(self):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.term_origin)
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
        self.cursor_show()
    def cursor_hide(self):
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()
    def cursor_show(self):
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()

    # cursor
    def getyx(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(sys.stdin.fileno())
        sys.stdout.write("\033[6n")
        sys.stdout.flush()
        buf = ""
        while True:
            char = sys.stdin.read(1)
            buf += char
            if char == "R":
                break
        # \033[{row};{col}R
        response = buf.strip("\033[").strip("R").split(";")
        y,x = int(response[0]), int(response[1])
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return (y,x)
    def set(self, y,x):
        sys.stdout.write(f'\033[{y};{x}H')
        sys.stdout.flush()
    def move(self, y,x):
        current_y, current_x = self.getyx()
        target_y = current_y + y if y is not None else current_y
        target_x = current_x + x if x is not None else current_x
        self.set(target_y, target_x)

    # clear
    def clear(self, mode=False):
        modes = {False: '2J', 'end': 'K', 'start': '1K', 'line': '2K', 'down': 'J', 'up': '1J'}
        char = modes.get(mode)
        if char is None:
            raise Exception(f'clear: unknown mode - {mode}')
        sys.stdout.write(f'\033[{char}')
        sys.stdout.flush()
    def clear_lines(self, count_lines=1):
        for _ in range(count_lines):
            sys.stdout.write('\x1b[1A')
            sys.stdout.write('\x1b[2K')
        sys.stdout.flush()

    # chars
    def getch(self):
        old_settings = termios.tcgetattr(self.fd)
        tty.setraw(self.fd)
        ch = sys.stdin.read(1)
        termios.tcsetattr(self.fd, termios.TCSADRAIN, old_settings)
        return ch
