import bmesh
from ..mv_utilities import *

MODULE_NAME = "Inverted Normals"
MODULE_FOO = "check_inverted_normals"
MODULE_GROUP = "topology"
MODULE_REPORT = "failed"
MODULE_INFO = "Проверка на наличие инвертированных полигонов"

def __set_foo_attributes(func):
    func.name = MODULE_NAME
    func.foo = MODULE_FOO
    func.group = MODULE_GROUP
    func.report = MODULE_REPORT
    func.info = MODULE_INFO
    return func

@__set_foo_attributes
@rest_editor_state
def check_inverted_normals(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue
        bad_faces = set()
        
        bm = bmesh.new()
        bm.from_mesh(object.data)
        bm.normal_update()
        
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        
        orig_normals = list(f.normal for f in object.data.polygons)
        copy_normals = list(f.normal for f in bm.faces)

        for face in bm.faces:
            orig_n = orig_normals[face.index]
            copy_n = copy_normals[face.index]
            if orig_n != copy_n:
                bad_faces.add(face.index)

        bm.clear()
        bm.free()
        object.data.update()

        if len(bad_faces) > 0:
            checked_objects[object.name] = ["FACE", bad_faces]
            success = set_warning_type(check_type)
    
    formate_result_string(context, check_type, success, checked_objects)