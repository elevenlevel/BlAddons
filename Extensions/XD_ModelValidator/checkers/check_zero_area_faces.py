from ..mv_utilities import *

def __set_foo_attributes(func):
    func.name = "Zero Area Faces"
    func.foo = "check_zero_area_faces"
    func.group = "topology"
    func.report = "failed"
    func.info = "Проверка на наличие полигонов с нулевой площадью"
    return func

@__set_foo_attributes
@rest_editor_state
def check_zero_area_faces(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue

        bpy.context.view_layer.objects.active = object

        bad_faces = set()
        bm = bmesh.new()
        bm.from_mesh(object.data)

        for face in bm.faces:
            if face.calc_area() == 0:
                bad_faces.add(face.index)

        bm.free()

        if len(bad_faces) > 0:
            checked_objects[object.name] = ["FACE", bad_faces]
            success = set_warning_type(check_type)

    formate_result_string(context, check_type, success, checked_objects)