import bmesh
from .. mv_utilities import *

MODULE_NAME = "Non Manifold Edges"
MODULE_FOO = "check_non_manifold_edges"
MODULE_GROUP = "topology"
MODULE_REPORT = "failed"
MODULE_INFO = "Если ребро имеет больше двух полигонов"

def __set_foo_attributes(func):
    func.name = MODULE_NAME
    func.foo = MODULE_FOO
    func.group = MODULE_GROUP
    func.report = MODULE_REPORT
    func.info = MODULE_INFO
    return func

@__set_foo_attributes
@rest_editor_state
def check_non_manifold_edges(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue

        bpy.context.view_layer.objects.active = object
        
        bad_edges = set()
        bm = bmesh.new()
        bm.from_mesh(object.data)

        for edge in bm.edges:
            if len(edge.link_faces) > 2:
                bad_edges.add(edge.index)
        
        bm.free()

        if len(bad_edges) > 0:
            checked_objects[object.name] = ["EDGE", bad_edges]
            success = set_warning_type(check_type)
        
    formate_result_string(context, check_type, success, checked_objects)