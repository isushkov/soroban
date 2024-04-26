import re
from colorama import Fore, Style, init
init(autoreset=True)

def todo(msg):
    p(f'[y]TODO:[c] {msg}..')
    exit(2)

def p(msg):
    print(z(msg))
def z(msg):
    replacements = {
        '[b]': Fore.BLUE,
        '[g]': Fore.GREEN,
        '[y]': Fore.YELLOW,
        '[r]': Fore.RED,
        '[x]': Fore.LIGHTBLACK_EX,
        '[c]': Style.RESET_ALL
    }
    for key, value in replacements.items():
        msg = msg.replace(key, value)
    return msg + Style.RESET_ALL
def b(msg):
    return colorize(msg, Fore.BLUE)
def g(msg):
    return colorize(msg, Fore.GREEN)
def y(msg):
    return colorize(msg, Fore.YELLOW)
def r(msg):
    return colorize(msg, Fore.RED)
def x(msg, color):
    return colorize(msg, Fore.LIGHTBLACK_EX)
def c(msg, color):
    return f'{color}{msg}{Style.RESET_ALL}'

def remove_colors(text):
    return re.sub(r'\x1b\[[0-9;]*m', '', text)
def get_fill_color(fill_color):
    if not fill_color:
        return ''
    return {
       'b': Fore.BLUE,
       'g': Fore.GREEN,
       'y': Fore.YELLOW,
       'r': Fore.RED,
       'x': Fore.LIGHTBLACK_EX
    }[fill_color]
# align
def ljust(text, width, fill_char=' ', fill_color=False):
    text_length = len(remove_colors(text))
    if text_length < width:
        color = get_fill_color(fill_color)
        return text + color+fill_char*(width - text_length)
    return text
def rjust(text, width, fill_char=' ', fill_color=False):
    text_length = len(remove_colors(text))
    if text_length < width:
        color = get_fill_color(fill_color)
        return color+fill_char*(width - text_length) + text
    return text
def edgesjust(text_left, text_right, width, fill_char=' ', fill_color=False):
    color = get_fill_color(fill_color)
    len_center  = width - len(remove_colors(text_left)) - len(remove_colors(text_right))
    return text_left + (color+len_center*fill_char) + text_right
def center(text, width, fill_char=' ', fill_color=False):
    text_length = len(remove_colors(text))
    total_padding = width - text_length
    padding_left = total_padding // 2
    padding_right = total_padding - padding_left
    color = get_fill_color(fill_color)
    return (color+fill_char*padding_left) + text + (color+fill_char*padding_right)
