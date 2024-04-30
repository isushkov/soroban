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
        self.w, self.h = shutil.get_terminal_size()
        self.tab = ' '
        self.sep = ' '
    # upds
    def upd_title(self, title, char='=', color='x'):
        self.title = c.z(c.ljust(c.z(f'[{color}]{char*9} {title} '), self.w, char, color))
    # render/display/upd
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
    # render/display/upd - magic (run if meth dosnt exist)
    def __getattr__(self, name):
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
    def wrap(self, text, width):
        # Функция для удаления цветов из текста
        def remove_colors(text):
            return re.sub(r'\x1B\[[^m]*m', '', text)
        text = c.z(text)
        bw_text = remove_colors(text)  # Текст без ANSI-цветов для подсчёта длины
        lines, line, current_length, i = [], '', 0, 0
        active_format = ''  # Для сохранения активного форматирования
        while i < len(text):
            if text[i] == '\x1b':  # Начало escape последовательности
                escape_seq = ''
                while text[i] not in 'mM':  # Читаем до конца последовательности (включительно символ 'm' или 'M')
                    escape_seq += text[i]
                    i += 1
                escape_seq += text[i]
                line += escape_seq  # Добавляем escape-последовательность в текущую строку
                active_format += escape_seq  # Обновляем активное форматирование
                i += 1
            else:
                if current_length == width:  # Проверка длины строки
                    lines.append(line)
                    line = active_format  # Начинаем новую строку с активного форматирования
                    current_length = 0  # Сброс счётчика длины для новой строки
                line += text[i]  # Добавляем символ в строку
                current_length += 1
                i += 1
        if line:  # Добавляем последнюю строку, если она не пуста
            lines.append(line)
        return lines
