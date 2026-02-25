import bmesh
from ..mv_utilities import *

MODULE_NAME = "check_ngons"
MODULE_FOO = "NGON Faces"
MODULE_GROUP = "topology"
MODULE_REPORT = "warning"
MODULE_INFO = "Проверка на наличие NGON полигонов"

def __set_foo_attributes(func):
    func.foo = MODULE_NAME
    func.name = MODULE_FOO
    func.group = MODULE_GROUP
    func.report = MODULE_REPORT
    func.info = MODULE_INFO
    return func

@__set_foo_attributes
@rest_editor_state
def check_ngons(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]
    
    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue

        bpy.context.view_layer.objects.active = object
    
        bad_faces = set()

        bm = bmesh.new()
        bm.from_mesh(object.data)
        
        for face in bm.faces:
            if len(face.verts) > 4:
                bad_faces.add(face.index)
        bm.free()

        if len(bad_faces) > 0:
            checked_objects[object.name] = ["FACE", bad_faces]
            success = set_warning_type(check_type)
    
    formate_result_string(context, check_type, success, checked_objects)

@__set_foo_attributes
@rest_editor_state
def _check_ngons(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]
    
    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue

        bpy.context.view_layer.objects.active = object
    
        bad_faces = set()

        for polygon in object.data.polygons:
            if len(polygon.vertices) > 4:
                bad_faces.add(polygon.index)

        if len(bad_faces) > 0:
            checked_objects[object.name] = ["FACE", bad_faces]
            success = set_warning_type(check_type)
    
    formate_result_string(context, check_type, success, checked_objects)