import math
import mathutils
from ..mv_utilities import *

MODULE_NAME = "Uncentered Pivots"
MODULE_FOO = "check_uncentered_pivots"
MODULE_GROUP = "general"
MODULE_REPORT = "warning"
MODULE_INFO = "Если Pivot не в центре объекта"

def __set_foo_attributes(func):
    func.name = MODULE_NAME
    func.foo = MODULE_FOO
    func.group = MODULE_GROUP
    func.report = MODULE_REPORT
    func.info = MODULE_INFO
    return func

@__set_foo_attributes
@rest_editor_state
def check_uncentered_pivots(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for object in select_check_entities("objects"):
        if object.type != "EMPTY" or object.type != "MESH":
            continue

        center = sum((mathutils.Vector(v.co) for v in object.data.vertices), mathutils.Vector())
        difference = math.dist(mathutils.Vector(object.location), center)
        print("Debug: {} center: {}".format(object.name, center))

        if difference > 0.0005:
            success = set_warning_type(check_type)

        checked_objects[object.name] = ["OBJECT"]
    
    formate_result_string(context, check_type, success, checked_objects)