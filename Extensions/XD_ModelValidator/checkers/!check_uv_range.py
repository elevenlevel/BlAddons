from ..mv_utilities import *

def __set_foo_attributes(func):
    func.name = "UV Range"
    func.foo = "check_uv_range"
    func.group = "uvs"
    func.report = "warning"
    func.info = "XXX"
    return func

@__set_foo_attributes
@rest_editor_state
def check_uv_range(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    bpy.ops.object.mode_set(mode = 'OBJECT')

    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue
        
        bad_faces = set()
        value = 0.00001

        for face in object.data.polygons:
            for loop in face.loop_indices:
                vert_uv = object.data.uv_layers[0].data[loop].uv
                if vert_uv[0] < -value or vert_uv[0] > 1+value or vert_uv[1] < -value or vert_uv[1] > 1+value:
                    bad_faces.add(face.index)

        checked_objects[object.name] = ["FACE", bad_faces]
    
    formate_result_string(context, check_type, success, checked_objects)