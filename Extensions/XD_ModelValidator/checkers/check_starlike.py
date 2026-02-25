import bmesh
from ..mv_utilities import *

MODULE_NAME = "Starlike Points"
MODULE_FOO = "check_starlike"
MODULE_GROUP = "topology"
MODULE_REPORT = "warning"
MODULE_INFO = "Когда в одну точку сходятся больше 4 ребер"

def __set_foo_attributes(func):
    func.name = MODULE_NAME
    func.foo = MODULE_FOO
    func.group = MODULE_GROUP
    func.report = MODULE_REPORT
    func.info = MODULE_INFO
    return func

@__set_foo_attributes
@rest_editor_state
def check_starlike(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue

        bpy.context.view_layer.objects.active = object

        bad_vertices = set()
        bm = bmesh.new()
        bm.from_mesh(object.data)
        
        for vertex in bm.verts:
            if len(vertex.link_faces) > 4:
                bad_vertices.add(vertex.index)

        bm.free()

        if len(bad_vertices) > 0:
            checked_objects[object.name] = ["VERT", bad_vertices]
            success = set_warning_type(check_type)
    
    formate_result_string(context, check_type, success, checked_objects)