import re
from colorama import Fore, Style, init
init(autoreset=True)

def cz(msg):
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
def cb(msg):
    return colorize(msg, Fore.BLUE)
def cg(msg):
    return colorize(msg, Fore.GREEN)
def cy(msg):
    return colorize(msg, Fore.YELLOW)
def cr(msg):
    return colorize(msg, Fore.RED)
def cx(msg, color):
    return colorize(msg, Fore.LIGHTBLACK_EX)
def cc(msg, color):
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
def c_center(text, width, fill_char=' ', fill_color=False):
    text_length = len(remove_colors(text))
    total_padding = width - text_length
    padding_left = total_padding // 2
    padding_right = total_padding - padding_left
    color = get_fill_color(fill_color)
    return color + fill_char * padding_left + text + color + fill_char * padding_right

def c_ljust(text, width, fillchar=' ', fill_color=False):
    text_length = len(remove_colors(text))
    if text_length < width:
        color = get_fill_color(fill_color)
        return text + color + fill_char * (width - text_length)
    return text
def c_rjust(text, width, fillchar=' ', fill_color=False):
    text_length = len(remove_colors(text))
    if text_length < width:
        color = get_fill_color(fill_color)
        return color + fill_char * (width - text_length) + text
    return text
