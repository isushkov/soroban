import re
import shutil
import src.helpers.colors as c

# render(attr, *args, **kwargs) : обновить и показать
# display(attr)                 : показать
# upd(attr, *args, **kwargs)    : обновить
# upd_attr_1(*args, **kwargs)   : specific upd()-logic for attr_1
# upd_attr_2(*args, **kwargs)   : specific upd()-logic for attr_2
class View():
    def __init__(self):
        self.w_term, self.h_term = shutil.get_terminal_size()
        self.w_user = 100
        self.w = self.calc_max_w()
        self.tab = ' '
        self.sep = ' '
    def calc_max_w(self):
        if not self.w_user:
            return self.w_term
        if self.w_user > self.w_term:
            return self.w_term
        return self.w_user
    # render/display/upd/calls
    def render(self, attr, *args, **kwargs):
        self.upd(attr, *args, **kwargs)
        self.display(attr)
    def display(self, attr):
        if not hasattr(self, attr):
            raise Exception(c.z(f"[r]ERROR: <View>.get('{attr}'):[c] attr dosnt exist."))
        print(c.z(getattr(self, attr)))
    def upd(self, attr, *args, **kwargs):
        method_name = 'upd_'+attr
        if not hasattr(self, method_name):
            raise Exception(c.z(f"[r]ERROR: <View>.upd_{attr}():[c] method dosnt exist."))
        # call meth()
        return getattr(self, method_name)(*args, **kwargs)
    # render/display/upd/calls - magic (exec if meth dosnt exist)
    def __getattr__(self, name):
        if name.startswith('calls_'):
            return 0
        parts = name.split('_')
        if len(parts) > 1:
            method_prefix = parts[0]
            attr_name = '_'.join(parts[1:])
            if method_prefix in ['display', 'upd', 'render']:
                # Генерируем функцию на лету
                def method(*args, **kwargs):
                    if method_prefix == 'display':
                        return self.display(attr_name)
                    elif method_prefix == 'upd':
                        return self.upd(attr_name, *args, **kwargs)
                    elif method_prefix == 'render':
                        return self.render(attr_name, *args, **kwargs)
                return method
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    # upds
    def upd_title(self, title, char='=', color='x'):
        self.title = self.dec_title(title, char, color)
    def dec_title(self, title, char='=', color='x'):
        return c.z(c.ljust(c.z(f'[{color}]{char*9} {title} '), self.w, char, color))
    # decorate
    def add_padding(self, text, padding, char=' '):
        left, top, right, bottom = padding
        lines = text.splitlines()
        padded_lines = [char * left + line + char * right for line in lines]
        top_padding = [char * (left + right + max(len(c.remove_colors(line)) for line in lines))] * top
        bottom_padding = [char * (left + right + max(len(c.remove_colors(line)) for line in lines))] * bottom
        return '\n'.join(top_padding + padded_lines + bottom_padding)
    def add_border(self, text, style=False, style_custom=False, color='', title=None):
        text = c.z(text)
        color = c.get_fill_color(color or 'c')
        if style == 'custom':
            h,v,tl,tr,bl,br = style_custom
        else:
            styles = {'classic': '-|++++', 'solid': '─│┌┐└┘', 'round': '─│╭╮╰╯', 'double': '═║╔╗╚╝'}
            h,v,tl,tr,bl,br = styles['solid'] if not style else styles[style]
        lines = text.splitlines()
        max_length = max(len(c.remove_colors(line)) for line in lines)
        max_length = max(max_length, len(title) if title else 0) # убедиться, что место есть для заголовка
        top_border = color + tl + (h * max_length) + tr
        bottom_border = color + bl + (h * max_length) + br
        padded_lines = [color + v + '[c]' + line + ' ' * (max_length - len(c.remove_colors(line))) + color + v for line in lines]
        res = '\n'.join([top_border] + padded_lines + [bottom_border])
        if title:
            title_text = title.center(max_length)
            top_border = color + tl + (h * max_length) + tr
            title_line = color + v + title_text + color + v
        else:
            top_border = color + tl + (h * max_length) + tr
        res = '\n'.join([top_border] + ([title_line] if title else []) + padded_lines + [bottom_border])
        if color:
            res = c.z(res)
        return res
    def merge_columns(self, *args, sep=' '):
        lines_lists = [arg.split('\n') for arg in args]
        if not lines_lists:
            return ''
        max_widths = [max(len(c.remove_colors(line)) for line in lines) for lines in lines_lists]
        max_lines = max(len(lines) for lines in lines_lists)
        merged_lines = []
        for i in range(max_lines):
            merged_line = ''
            for index, lines in enumerate(lines_lists):
                if i < len(lines):
                    line = lines[i] # добавляем строку из текущей колонки, если она существует
                    # пробелы для выравнивания до максимальной ширины колонки
                    merged_line += line.ljust(max_widths[index])
                # пробелы между колонками
                if index < len(lines_lists) - 1:
                    merged_line += sep
            merged_lines.append(merged_line.rstrip())
        return '\n'.join(merged_lines)
    def wrap(self, text, width):
        text = c.z(text)
        bw_text = c.remove_colors(text)
        lines, line, current_length, i = [], '', 0, 0
        active_format = '' # для сохранения активного форматирования
        while i < len(text):
            if text[i] == '\x1b': # начало последовательности
                escape_seq = ''
                while text[i] not in 'mM': # конец последовательности
                    escape_seq += text[i]
                    i += 1
                escape_seq += text[i]
                line += escape_seq  # добавляем escape-последовательность в текущую строку
                active_format += escape_seq # обновляем активное форматирование
                i += 1
            else:
                if current_length == width:
                    lines.append(line)
                    line = active_format # начинаем новую строку с активного форматирования
                    current_length = 0 # сброс счётчика длины для новой строки
                line += text[i] # добавляем символ в строку
                current_length += 1
                i += 1
        if line: # добавляем последнюю строку, если она не пуста
            lines.append(line)
        return lines
