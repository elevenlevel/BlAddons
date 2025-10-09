from ..mv_utilities import *

def __set_foo_attributes(func):
    func.name = "Postfix Numbers"
    func.foo = "check_postfix_numbers"
    func.group = "naming"
    func.report = "warning"
    func.info = "Проверка на числа в конце имени"
    return func

@__set_foo_attributes
@rest_editor_state
def check_postfix_numbers(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for object in select_check_entities("objects"):
        if object.name[-1].isdigit():
            success = set_warning_type(check_type)
            checked_objects[object.name] = ["OBJECT"]
    
    for collection in select_check_entities("collections"):
        if collection.name[-1].isdigit():
            success = set_warning_type(check_type)
            checked_objects[collection.name] = ["COLL"]
    
    formate_result_string(context, check_type, success, checked_objects)