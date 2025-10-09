from ..mv_utilities import *

def __set_foo_attributes(func):
    func.name = "Missing UVs"
    func.foo = "check_missing_uvs"
    func.group = "uvs"
    func.report = "warning"
    func.info = "Если объект не имеет uv атрибута"
    return func

@__set_foo_attributes
@rest_editor_state
def check_missing_uvs(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue

        bpy.context.view_layer.objects.active = object
        
        if len(object.data.uv_layers) == 0:
            success = set_warning_type(check_type)
            checked_objects[object.name] = ["OBJECT"]
    
    formate_result_string(context, check_type, success, checked_objects)