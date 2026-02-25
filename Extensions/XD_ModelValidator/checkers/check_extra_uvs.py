from ..mv_utilities import *

# Единый источник истины
MODULE_NAME = "Extra UVs"
MODULE_FOO = "check_extra_uvs"
MODULE_GROUP = "uvs"
MODULE_REPORT = "warning"
MODULE_INFO = "Если объект имеет больше 2х uv атрибутов"

def __set_foo_attributes(func):
    func.name = MODULE_NAME
    func.foo = MODULE_FOO
    func.group = MODULE_GROUP
    func.report = MODULE_REPORT
    func.info = MODULE_INFO
    return func

@__set_foo_attributes
@rest_editor_state
def check_extra_uvs(context, check_type, success="[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue

        bpy.context.view_layer.objects.active = object
        
        if len(object.data.uv_layers) > 2:
            checked_objects[object.name] = ["OBJECT"]
            success = set_warning_type(check_type)
    
    formate_result_string(context, check_type, success, checked_objects)