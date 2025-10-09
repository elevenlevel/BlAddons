from ..mv_utilities import *

def __set_foo_attributes(func):
    func.name = "Lowercase Names"
    func.foo = "check_lowercase_names"
    func.group = "naming"
    func.report = "warning"
    func.info = "Если все символы имени в нижнем регистре"
    return func

@__set_foo_attributes
@rest_editor_state
def check_lowercase_names(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for object in select_check_entities("objects"):
        if object.name.islower():
            success = set_warning_type(check_type)
            checked_objects[object.name] = ["OBJECT"]
    
    for collection in select_check_entities("collections"):
        if collection.name.islower():
            success = set_warning_type(check_type)
            checked_objects[collection.name] = ["COLL"]
    
    formate_result_string(context, check_type, success, checked_objects)