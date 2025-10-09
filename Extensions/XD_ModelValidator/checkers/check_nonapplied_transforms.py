from ..mv_utilities import *

def __set_foo_attributes(func):
    func.name = "Nonapplied Transforms"
    func.foo = "check_nonapplied_transforms"
    func.group = "general"
    func.report = "warning" # failed, warning
    func.info = "Если Location и Rotation объекта не равны нулю или Scale объекта не равен единице"
    return func

@__set_foo_attributes
@rest_editor_state
def check_nonapplied_transforms(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    ZERO_VEC = mathutils.Vector((0.0, 0.0, 0.0))
    ONE_VEC = mathutils.Vector((1.0, 1.0, 1.0))

    for object in select_check_entities("objects"):
        loc = object.location
        rot = object.rotation_euler
        scale = object.scale
        
        if loc != ZERO_VEC or rot != ZERO_VEC or scale != ONE_VEC:
            success = set_warning_type(check_type)
            checked_objects[object.name] = ["OBJECT"]
    
    formate_result_string(context, check_type, success, checked_objects)