from ..mv_utilities import *

def __set_foo_attributes(func):
    func.name = "Extra Symbols"
    func.foo = "check_extra_symbols"
    func.group = "naming"
    func.report = "warning"
    func.info = "Проверка на всякие непонятные символы в имени"
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