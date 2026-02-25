import mathutils
from ..mv_utilities import *

MODULE_NAME = "Nonapplied Transforms"
MODULE_FOO = "check_nonapplied_transforms"
MODULE_GROUP = "general"
MODULE_REPORT = "warning" # failed, warning
MODULE_INFO = "Если Location и Rotation объекта не равны нулю или Scale объекта не равен единице"

def __set_foo_attributes(func):
    func.name = MODULE_NAME
    func.foo = MODULE_FOO
    func.group = MODULE_GROUP
    func.report = MODULE_REPORT
    func.info = MODULE_INFO
    return func

@__set_foo_attributes
@rest_editor_state
def check_nonapplied_transforms(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    ZERO_LOC = mathutils.Vector((0.0, 0.0, 0.0))
    ZERO_EULER = mathutils.Euler((0.0, 0.0, 0.0), 'XYZ')
    ONE_SCALE = mathutils.Vector((1.0, 1.0, 1.0))

    for object in select_check_entities("objects"):
        loc = object.location
        rot = object.rotation_euler
        scale = object.scale
        
        if loc != ZERO_LOC or rot != ZERO_EULER or scale != ONE_SCALE:
            success = set_warning_type(check_type)
            checked_objects[object.name] = ["OBJECT"]
    
    formate_result_string(context, check_type, success, checked_objects)