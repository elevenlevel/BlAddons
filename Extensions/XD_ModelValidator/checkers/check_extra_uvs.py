from ..mv_utilities import *

def __set_foo_attributes(func):
    func.name = "Extra UVs"
    func.foo = "check_extra_uvs"
    func.group = "uvs"
    func.report = "warning"
    func.info = "Если объект имеет больше 2х uv атрибутов"
    return func

@__set_foo_attributes
@rest_editor_state
def check_extra_uvs(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue

        bpy.context.view_layer.objects.active = object
        
        if len(object.data.uv_layers) > 2:
            checked_objects[object.name] = ["OBJECT"]
            success = set_warning_type(check_type)
    
    formate_result_string(context, check_type, success, checked_objects)