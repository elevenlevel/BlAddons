import sys
import os
import importlib
from os import listdir, path

# добавляем текущий путь в sys.path
# sys.path.insert(0, os.path.abspath(os.path.dirname(__file__))) # это вызывало warning

checkbox_list = {} # словарь свойств модулей

# импорт модулей из папки checkers
current_dir = path.dirname(__file__)

for file in listdir(current_dir):
    if file.endswith('.py') and file != '__init__.py' and "!" not in file:
        module_name = file[:-3]
        exec(f"from .{module_name} import {module_name}")

        checkbox_list[globals()[module_name].name] = { "foo":globals()[module_name].foo,
                                                "group":globals()[module_name].group,
                                                "report":globals()[module_name].report,
                                                "function": globals()[module_name],
                                                "info":globals()[module_name].info}

for filename in os.listdir(current_dir):
    if (filename.endswith('.py') and 
        filename != '__init__.py' and
        '!' not in filename):
        
        module_name = filename[:-3]  # имя без .py
        
        # Импортируем модуль через importlib (безопасно)
        module = importlib.import_module(f'.{module_name}', package=__package__)
        
        # Добавляем в checkbox_list, если у модуля есть атрибут name
        if hasattr(module, 'name'):
            checkbox_list[module.name] = {
                'foo': getattr(module, 'foo', None),
                'group': getattr(module, 'group', None),
                'report': getattr(module, 'report', None),
                'info': getattr(module, 'info', None)
            }

# Обязательно объявляем __all__
__all__ = ['checkbox_list']