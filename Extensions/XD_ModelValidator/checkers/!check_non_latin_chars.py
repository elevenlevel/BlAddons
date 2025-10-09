from .. mv_utilities import *

def __set_foo_attributes(func):
    func.name = "Non Latin Chars"
    func.foo = "check_non_latin_chars"
    func.group = "naming"
    func.report = "failed"
    func.info = "Если в имени используется не латинский алфавит"
    return func

@__set_foo_attributes
@rest_editor_state
def check_non_latin_chars(context, check_type, success = "[SUCCESS]"):
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