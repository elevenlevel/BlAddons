import bmesh
from ..mv_utilities import *

MODULE_NAME = "Distorted Faces"
MODULE_FOO = "check_distorted_faces"
MODULE_GROUP = "topology"
MODULE_REPORT = "warning"
MODULE_INFO = "Проверка на наличие искаженных полигонов"

def __set_foo_attributes(func):
    func.foo = MODULE_FOO
    func.name = MODULE_NAME
    func.group = MODULE_GROUP
    func.report = MODULE_REPORT
    func.info = MODULE_INFO
    return func

@__set_foo_attributes
@rest_editor_state
def check_distorted_faces(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]
    
    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue

        bpy.context.view_layer.objects.active = object
    
        bad_faces = set()

        bm = bmesh.new()
        bm.from_mesh(object.data)

        for face in bm.faces:
            if len(face.verts) < 3:
                continue

            edges_len = []
            for edge in face.edges:
                edges_len.append(edge.calc_length())

            avg_len = sum(edges_len) / len(edges_len)
            min_val = min(edges_len)
            max_val = max(edges_len)

            if (max_val - min_val) > 0.99 * avg_len:
                bad_faces.add(face.index)

        bm.free()

        if len(bad_faces) > 0:
            checked_objects[object.name] = ["FACE", bad_faces]
            success = set_warning_type(check_type)
    
    formate_result_string(context, check_type, success, checked_objects)