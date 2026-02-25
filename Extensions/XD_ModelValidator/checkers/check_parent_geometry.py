from ..mv_utilities import *

MODULE_NAME = "Parent Geometry"
MODULE_FOO = "check_parent_geometry"
MODULE_GROUP = "general"
MODULE_REPORT = "warning"
MODULE_INFO = "Проверка на вложенные объекты"

def __set_foo_attributes(func):
    func.name = MODULE_NAME
    func.foo = MODULE_FOO
    func.group = MODULE_GROUP
    func.report = MODULE_REPORT
    func.info = MODULE_INFO
    return func

@__set_foo_attributes
@rest_editor_state
def check_parent_geometry(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    bad_objects = set()

    for object in select_check_entities("objects"):
        if object.parent != None:
            bad_objects.add(object)
            success = set_warning_type(check_type)
            checked_objects[object.name] = ["OBJECT"]
    
    formate_result_string(context, check_type, success, checked_objects)