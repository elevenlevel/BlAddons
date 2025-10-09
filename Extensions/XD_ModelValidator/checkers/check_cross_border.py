from ..mv_utilities import *

def __set_foo_attributes(func):
    func.name = "Cross Border"
    func.foo = "check_cross_border"
    func.group = "uvs"
    func.report = "warning"
    func.info = "Проверка UVs объектов на пересечения границ UV"
    return func

@__set_foo_attributes
@rest_editor_state
def check_cross_border(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for object in select_check_entities("objects"):
        if object.type != "MESH":
            return
        
        bpy.context.view_layer.objects.active = object

        # проверка есть ли у объекта uv вообще
        if len(object.data.uv_layers) == 0:
            checked_objects[object.name + " NO UVs!!!"] = ["OBJECT"]
            success = "[FAILED]"
            continue

        bad_faces = []

        bm = bmesh.new()
        bm.from_mesh(object.data)
        uv_lay = bm.loops.layers.uv.active

        for face in bm.faces:
            face_floored_uv = set()
            
            for loop in face.loops: # доступ к uv координатам каждой вершины
                uv = loop[uv_lay].uv
                floored_uv = math.floor(uv[0]), math.floor(uv[1])
                face_floored_uv.add(floored_uv)
            
            if len(face_floored_uv) > 1:
                bad_faces.append(face.index)

        bm.free()

        if len(bad_faces) > 0:
            checked_objects[object.name] = ["FACE", bad_faces]
            success = set_warning_type(check_type)
    
        formate_result_string(context, check_type, success, checked_objects)

@__set_foo_attributes
@rest_editor_state
def _check_cross_border(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for object in select_check_entities("objects"):
        if object.type != "MESH":
            return
        
        bpy.context.view_layer.objects.active = object

        if len(object.data.uv_layers) == 0:
            checked_objects[object.name + " NO UVs!!!"] = ["OBJECT"]
            success = "[FAILED]"
            continue

        bad_faces = []

        for face in object.data.polygons:
            face_floored_u = [] # все U компоненты полигона [0, 0, 0, 0]
            face_floored_v = [] # все V компоненты полигона [0, 0, 0, 0]
            
            for loop in face.loop_indices: # доступ к uv координатам каждой вершины
                floored_u = []
                floored_v = []
                
                for index, vert_uv in enumerate(object.data.uv_layers[0].data[loop].uv): # доступ к каждой компоненте координаты по очереди
                    if index==0:
                        floored_u.append(math.floor(vert_uv))
                    else:
                        floored_v.append(math.floor(vert_uv))
                
                face_floored_u.append(floored_u[0])
                face_floored_v.append(floored_v[0])
            
            face_floored_u = set(face_floored_u)
            face_floored_v = set(face_floored_v)
            
            if (len(face_floored_u) > 1) or len(face_floored_v) > 1:
                bad_faces.append(face.index)

        if len(bad_faces) > 0:
            checked_objects[object.name] = ["FACE", bad_faces]
            success = set_warning_type(check_type)
    
        formate_result_string(context, check_type, success, checked_objects)