from ..mv_utilities import *

def __set_foo_attributes(func):
    func.name = "On Border"
    func.foo = "check_on_border"
    func.group = "uvs"
    func.report = "warning"
    func.info = "Когда uv вертексы очень близко к границам UV"
    return func

@__set_foo_attributes
@rest_editor_state
def check_on_border(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue

        bpy.context.view_layer.objects.active = object

        if len(object.data.uv_layers) == 0:
            checked_objects[object.name + " NO UVs!!!"] = ["OBJECT"]
            success = "[FAILED]"
            continue
        
        bad_faces = set()

        bm = bmesh.new()
        bm.from_mesh(object.data)
        uv_lay = bm.loops.layers.uv.active

        for face in bm.faces:
            for loop in face.loops: # доступ к uv координатам каждой вершины
                uv = loop[uv_lay].uv
            
                if abs(int(uv[0]) - uv[0]) < 0.00001 or abs(int(uv[1]) - uv[1]) < 0.00001:
                    bad_faces.add(face.index)

        bm.free()

        if len(bad_faces) > 0:
            checked_objects[object.name] = ["FACE", bad_faces]
            success = set_warning_type(check_type)
    
    formate_result_string(context, check_type, success, checked_objects)

@__set_foo_attributes
@rest_editor_state
def _check_on_border(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue

        bpy.context.view_layer.objects.active = object

        if len(object.data.uv_layers) == 0:
            checked_objects[object.name + " NO UVs!!!"] = ["OBJECT"]
            success = "[FAILED]"
            continue
        
        bad_faces = set()

        for face in object.data.polygons:
            face_u = [] # все U компоненты полигона [0, 0, 0, 0]
            face_v = [] # все V компоненты полигона [0, 0, 0, 0]
            for loop in face.loop_indices: # доступ к вершине согласно порядку в полигоне
                face_u.append(object.data.uv_layers[0].data[loop].uv[0])
                face_v.append(object.data.uv_layers[0].data[loop].uv[1])
            
            for i, loop in enumerate(face.loop_indices):
                if abs(int(face_u[i]) - face_u[i]) < 0.00001 or abs(int(face_v[i]) - face_v[i]) < 0.00001:
                    bad_faces.add(face.index)

        if len(bad_faces) > 0:
            checked_objects[object.name] = ["FACE", bad_faces]
            success = set_warning_type(check_type)
    
    formate_result_string(context, check_type, success, checked_objects)