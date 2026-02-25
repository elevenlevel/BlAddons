from ..mv_utilities import *

# Единый источник истины
MODULE_NAME = "Empty Nulls"
MODULE_FOO = "check_empty_nulls"
MODULE_GROUP = "general"
MODULE_REPORT = "warning"
MODULE_INFO = "Если в пустышке нет объектов"

def __set_foo_attributes(func):
    func.name = MODULE_NAME
    func.foo = MODULE_FOO
    func.group = MODULE_GROUP
    func.report = MODULE_REPORT
    func.info = MODULE_INFO
    return func

@__set_foo_attributes
@rest_editor_state
def check_empty_nulls(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]
    
    for object in select_check_entities("objects"):
        if object.type != "EMPTY":
            continue

        success = set_warning_type(check_type)
        checked_objects[object.name] = ["EMPTY"]
    
    formate_result_string(context, check_type, success, checked_objects)