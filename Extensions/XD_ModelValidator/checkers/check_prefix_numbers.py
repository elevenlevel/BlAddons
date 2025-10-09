from ..mv_utilities import *

def __set_foo_attributes(func):
    func.name = "Prefix Numbers"
    func.foo = "check_prefix_numbers"
    func.group = "naming"
    func.report = "warning"
    func.info = "Проверка на числа в начале имени"
    return func

@__set_foo_attributes
@rest_editor_state
def check_prefix_numbers(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for object in select_check_entities("objects"):
        if object.name[0].isdigit():
            success = set_warning_type(check_type)
            checked_objects[object.name] = ["OBJECT"]
    
    for collection in select_check_entities("collections"):
        if collection.name[0].isdigit():
            success = set_warning_type(check_type)
            checked_objects[collection.name] = ["COLL"]
    
    formate_result_string(context, check_type, success, checked_objects)