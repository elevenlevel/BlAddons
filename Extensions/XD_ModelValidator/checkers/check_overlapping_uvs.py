from ..mv_utilities import *

def __set_foo_attributes(func):
    func.name = "Overlapping UVs (slow)"
    func.foo = "check_overlapping_uvs"
    func.group = "uvs"
    func.report = "warning"
    func.info = "Проверка на перекрытие одних uv полигонов другими"
    return func

@__set_foo_attributes
@rest_editor_state
def check_overlapping_uvs(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    # включаем синхронизацию выделений UV
    tool_settings = context.scene.tool_settings
    uv_sync = tool_settings.use_uv_select_sync

    if not uv_sync:
        tool_settings.use_uv_select_sync = True

    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue

        bpy.context.view_layer.objects.active = object

        if len(object.data.uv_layers) == 0:
            checked_objects[object.name + " NO UVs!!!"] = ["OBJECT"]
            success = "[FAILED]"
            continue

        selected_polys = [p for p in object.data.polygons if p.select]
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.select_overlap(extend=False)
        bpy.ops.object.mode_set(mode='OBJECT')

        #bad_vertices = set()
        bad_faces = set()

        bm = bmesh.new()
        bm.from_mesh(object.data)

        for face in bm.faces:
            if face.select:
                bad_faces.add(face.index)
                face.select = False

                if face.index in selected_polys:
                    face.select = True
                    
        bm.free()

        # возвращаем назад значение синхронизации выделений UV
        tool_settings.use_uv_select_sync = uv_sync

        if len(bad_faces) > 0:
            checked_objects[object.name] = ["FACE", bad_faces]
            success = set_warning_type(check_type)
    
    formate_result_string(context, check_type, success, checked_objects)


def __check_overlapping_uvs(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    # включаем синхронизацию выделений UV
    tool_settings = context.scene.tool_settings
    uv_sync = tool_settings.use_uv_select_sync

    if not uv_sync:
        tool_settings.use_uv_select_sync = True

    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue
        
        bpy.ops.object.select_all(action='DESELECT')
        bad_faces = set()

        bm = bmesh.new()
        bm.from_mesh(object.data)
        uv_layer = bm.loops.layers.uv[0] # uv0

        for face in bm.faces:
            for face2 in bm.faces:
                if face.index == face2.index:
                    continue
                for loop in face.loops:
                    point = loop[uv_layer].uv
                    result = ray_casting(object, point, face)
                    print("face", face.index, ": result", result)

        bm.free()

        # возвращаем назад значение синхронизации выделений UV
        tool_settings.use_uv_select_sync = uv_sync

        if len(bad_faces) > 0:
            checked_objects[object.name] = ["FACE", bad_faces]
            success = set_warning_type(check_type)
    
    formate_result_string(context, check_type, success, checked_objects)

def ray_casting(object, point, polygon):
    # преобразуем точку и полигон в мировые координаты
    point_world = object.matrix_world * mathutils.Vector(point)
    polygon_world = [object.matrix_world * mathutils.Vector(v) for v in polygon.verts]
    poly_center = sum(polygon_world, mathutils.Vector()) / len(polygon_world)
    # выбираем направление для луча
    direction = (point - poly_center).normalize()

    # проводим луч из точки в выбранном направлении
    ray = mathutils.Vector(point_world) + direction

    # посчитаем количество пересечений луча с ребрами полигона
    intersections = 0
    for i in range(len(polygon_world)):
        v1 = polygon_world[i]
        v2 = polygon_world[(i + 1) % len(polygon_world)]
        if intersect(ray, v1, v2):
            intersections += 1
        
    # если количество пересечений четное, то точка находится вне полигона
    if intersections % 2 == 0:
        return False
    else:
        return True

def intersect(ray, v1, v2):
    # проверяем, пересекает ли луч отрезок между v1 и v2
    denominator = (v2 - v1).dot(ray)
    if denominator == 0:
        return False
    t = (ray - v1).dot(v2 - v1) / denominator
    if t > 0 and t < 1:
        return True
    return False