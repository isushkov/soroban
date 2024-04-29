import shutil
# src/helpers
import src.helpers.colors as c

# render(attr, *args, **kwargs) : обновить и показать
# display(attr)                 : показать
# upd(attr, *args, **kwargs)    : обновить
# upd_attr_1(*args, **kwargs)   : specific upd()-logic for attr_1
# upd_attr_2(*args, **kwargs)   : specific upd()-logic for attr_2
class View():
    def __init__(self):
        self.w, _ = shutil.get_terminal_size()
        self.tab = ' '
        self.sep = ' '
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
            method_prefix = parts[0]  # например, 'display', 'upd', 'render'
            attr_name = '_'.join(parts[1:])  # например, 'title', 'asdf'

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
        print(c.ljust(c.z(f'{color}{char*9} {title} '), self.w, char, color))
