from ..mv_utilities import *

def __set_foo_attributes(func):
    func.name = "Empty Nulls"
    func.foo = "check_empty_nulls"
    func.group = "general"
    func.report = "warning"
    func.info = "Если в пустышке нет объектов"
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