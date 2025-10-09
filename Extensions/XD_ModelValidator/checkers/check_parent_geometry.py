from ..mv_utilities import *

def __set_foo_attributes(func):
    func.name = "Parent Geometry"
    func.foo = "check_parent_geometry"
    func.group = "general"
    func.report = "warning"
    func.info = "Проверка на вложенные объекты"
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