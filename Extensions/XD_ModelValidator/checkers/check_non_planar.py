from ..mv_utilities import *

def __set_foo_attributes(func):
    func.foo = "check_non_planar"
    func.name = "Non Planar"
    func.group = "topology"
    func.report = "warning"
    func.info = "Проверка на наличие не плоских полигонов"
    return func

@__set_foo_attributes
@rest_editor_state
def check_non_planar(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]
    
    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue

        bpy.context.view_layer.objects.active = object
    
        bad_faces = set()

        bm = bmesh.new()
        bm.from_mesh(object.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        for face in bm.faces:
            if len(face.verts) < 4:
                continue  # Треугольники всегда плоские
            
            # Получаем координаты вершин полигона
            verts = [bm.verts[v.index].co for v in face.verts]

            # Вычисляем векторы между вершинами
            vec1 = verts[1] - verts[0]
            vec2 = verts[2] - verts[0]

            # Вычисляем нормаль к плоскости, образованной первыми тремя вершинами
            normal = vec1.cross(vec2)

            # Проверяем, что все остальные вершины лежат в той же плоскости
            for vert in verts[3:]:
                vec = vert - verts[0]
                if abs(normal.dot(vec)) > 0.001:
                    bad_faces.add(face.index)

        bm.free()

        if len(bad_faces) > 0:
            checked_objects[object.name] = ["FACE", bad_faces]
            success = set_warning_type(check_type)
    
    formate_result_string(context, check_type, success, checked_objects)