import sys, os
from os import listdir, path

# добавляем текущий путь в sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

checkbox_list = {} # словарь свойств модулей

# импорт модулей из папки checkers
current_dir = path.dirname(__file__)
for file in listdir(current_dir):
    if file.endswith('.py') and file != '__init__.py' and "!" not in file:
        name = file[:-3]
        exec(f"from .{name} import {name}")

        checkbox_list[globals()[name].name] = { "foo":globals()[name].foo,
                                                "group":globals()[name].group,
                                                "report":globals()[name].report,
                                                "info":globals()[name].info}