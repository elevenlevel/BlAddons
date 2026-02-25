from ..mv_utilities import *

# Единый источник истины
MODULE_NAME = "Extra Symbols"
MODULE_FOO = "check_extra_symbols"
MODULE_GROUP = "naming"
MODULE_REPORT = "warning"
MODULE_INFO = "Проверка на всякие непонятные символы в имени"

def __set_foo_attributes(func):
    func.name = MODULE_NAME
    func.foo = MODULE_FOO
    func.group = MODULE_GROUP
    func.report = MODULE_REPORT
    func.info = MODULE_INFO
    return func

@__set_foo_attributes
@rest_editor_state
def check_extra_symbols(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    #cyr_chars = "абвгдеёжзиклмнопрстуфхцчшщъыьэюя"
    latin_chars = " abcdefghijklmnopqrstuvwxyz0123456789!()_-."

    def has_non_latin_chars(s):
        return any(c not in latin_chars for c in s)
    
    for object in select_check_entities("objects"):
        if has_non_latin_chars(object.name.lower()):
            success = set_warning_type(check_type)
            checked_objects[object.name] = ["OBJECT"]
    
    for collection in select_check_entities("collections"):
        if has_non_latin_chars(collection.name.lower()):
            checked_objects[collection.name] = ["COLL"]
            success = set_warning_type(check_type)
    
    formate_result_string(context, check_type, success, checked_objects)