from ..mv_utilities import *

MODULE_NAME = "Prefix Numbers"
MODULE_FOO = "check_prefix_numbers"
MODULE_GROUP = "naming"
MODULE_REPORT = "warning"
MODULE_INFO = "Проверка на числа в начале имени"

def __set_foo_attributes(func):
    func.name = MODULE_NAME
    func.foo = MODULE_FOO
    func.group = MODULE_GROUP
    func.report = MODULE_REPORT
    func.info = MODULE_INFO
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