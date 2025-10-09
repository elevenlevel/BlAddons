import bpy
from mathutils import Euler, Matrix, Vector
from math import radians

def reset_mesh_position(obj, bm): # двигаем меш объекта в центр сцены
    obj_location = obj.location.copy()
    world_matrix = obj.matrix_world
    inverse_world_matrix = world_matrix.inverted_safe()
    
    for v in bm.verts:
        local_coord = v.co
        world_coord = world_matrix @ local_coord
        world_coord -= obj_location
        v.co = inverse_world_matrix @ world_coord

def set_mesh_position(obj, bm, coord=(0.0, 0.0, 0.0)): # двигаем меш объекта в указанные координаты
    obj_location = obj.location.copy()
    world_matrix = obj.matrix_world
    inverse_world_matrix = world_matrix.inverted_safe()
    
    for v in bm.verts:
        local_coord = v.co
        world_coord = world_matrix @ local_coord
        world_coord -= obj_location
        v.co = inverse_world_matrix @ world_coord
        v.co += coord

def reset_obj_position(obj): # двигаем объект вместе с пивотом в центр сцены
    obj.location = (0, 0, 0)

def set_obj_position(obj, new_coord=(0.0,0.0,0.0)): # двигаем объект вместе с пивотом в указанные координаты
    obj.location = new_coord

def reset_obj_rotation(obj): # сбрасываем заданный поворот объекта
    obj_rotation = obj.rotation_euler.copy()
    obj_location = obj.location.copy()
    rotation_matrix_3x3 = Euler(obj_rotation).to_matrix().to_3x3().inverted_safe()
    rotation_matrix_4x4 = rotation_matrix_3x3.to_4x4()
    obj.matrix_world = rotation_matrix_4x4 @ obj.matrix_world
    obj.location = obj_location

def set_obj_rotation(obj, pass_children=True, angle=(0.0, 0.0, 0.0)): # задаем новый поворот объекта
    if pass_children:
        if obj.parent != None: return

    obj_rotation = obj.rotation_euler.copy()
    
    euler_angles = (radians(angle[0]), radians(angle[1]), radians(angle[2]))
    add_rotation_matrix = Euler(euler_angles).to_matrix()
    
    obj_location = obj.location.copy()
    obj_rotation_matrix = Euler(obj_rotation).to_matrix()
    
    summ_of_matrices = obj_rotation_matrix @ add_rotation_matrix
    rotation_matrix_3x3 = summ_of_matrices.to_3x3().inverted_safe()
    rotation_matrix_4x4 = rotation_matrix_3x3.to_4x4()
    obj.matrix_world = rotation_matrix_4x4 @ obj.matrix_world
    obj.location = obj_location

def set_obj_rotation_local(obj, angle=(0.0, 0.0, 0.0)): # задаем новый поворот объекта локально
    angle_rev = (radians(-angle[0]), radians(-angle[1]), radians(-angle[2]))

    world_p = obj.matrix_world.translation.copy()

    new_rotation_m_3x3 = Euler(angle_rev).to_matrix().to_3x3()
    new_rotation_m_4x4 = new_rotation_m_3x3.to_4x4()
    obj.matrix_world = new_rotation_m_4x4
    obj.matrix_world.translation = world_p

def rotate_obj_world(obj, angle=(0.0, 0.0, 0.0)): # добавляем поворот объекта глобально
    angle = (radians(-angle[0]), radians(-angle[1]), radians(-angle[2]))
    old_matrix = obj.matrix_world.copy()
    new_rotation_m_3x3 = Euler(angle).to_matrix().to_3x3()
    new_rotation_m_4x4 = new_rotation_m_3x3.to_4x4()
    obj.matrix_world = new_rotation_m_4x4 @ old_matrix

def rotate_obj_local(obj, angle=(0.0, 0.0, 0.0)): # добавляем поворот объекта локально
    angle_rev = (radians(-angle[0]), radians(-angle[1]), radians(-angle[2]))

    world_p = obj.matrix_world.translation.copy()

    new_rotation_m_3x3 = Euler(angle_rev).to_matrix().to_3x3()
    new_rotation_m_4x4 = new_rotation_m_3x3.to_4x4()
    obj.matrix_world @= new_rotation_m_4x4
    obj.matrix_world.translation = world_p

def reset_pivot_rotation(obj): # сбрасываем поворот пивота
    mesh = obj.data #ob.data tmp_me

    import bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    old_rotation = obj.rotation_euler.copy()
    reset_obj_rotation(obj)
    rotation_matrix = Euler(old_rotation).to_matrix()

    for v in bm.verts:
        v.co = rotation_matrix @ v.co
    
    bm.to_mesh(mesh)
    bm.free()

def add_pivot_rotation(obj, angle=(0.0, 0.0, 0.0)): # задаем новый поворот пивота
    angle_rev = (-angle[0], -angle[1], -angle[2])
    angle_mtx = Euler((radians(angle[0]), radians(angle[1]), radians(angle[2]))).to_matrix()
    mesh = obj.data #ob.data tmp_me
    rotate_obj_local(obj, angle)

    import bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh)

    for v in bm.verts:
        v.co = angle_mtx @ v.co
        
    bm.to_mesh(mesh)
    bm.free()

def rotate_mesh_world(obj, mesh, angle=(0.0, 0.0, 0.0)):
    #mesh = obj.data
    rotation_matrix = Euler((radians(angle[0]), radians(angle[1]), radians(angle[2]))).to_matrix()
    world_matrix = obj.matrix_world.copy()
    #world_matrix = obj.matrix_world.copy() @ angle_mtx.to_3x3().to_4x4()

    import bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh)

    for v in bm.verts:
        world_coord = world_matrix @ v.co
        rotated_coord = rotation_matrix @ world_coord
        v.co = (world_matrix.inverted() @ rotated_coord)
        #v.co = world_matrix @ v.co
    
    bm.to_mesh(mesh)
    bm.free()


def xd_convert_rotation_to_unity(obj, mesh):
    #obj_copy = obj.copy()
    rotate_mesh_world(obj, mesh,(-90.0, 0.0, 0.0))
    if obj.parent == None:
        add_pivot_rotation(obj, angle=(-90.0, 0.0, 0.0))
    pass

'''
def xd_edit_objects_decorator(func): # ЭТОТ КОД ОКАЗАЛСЯ ВПОЛНЕ РАБОЧИМ, НО НАДО ПОВОРАЧИВАТЬ ПИВОТЫ ДОЧЕРНИХ ОБЪЕКТОВ
    def transformate_objects(euler_angles=(0.0, 0.0, 0.0)):
        import bpy
        all_objects = bpy.data.objects
        active_object = bpy.context.active_object
        selected_objects = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')

        rad_angles = (radians(euler_angles[0]), radians(euler_angles[1]), radians(euler_angles[2]))
        
        for obj in all_objects:
            # print(obj.name, obj.parent)
            obj.select_set(False)
            if obj.parent == None:
                obj.rotation_euler = rad_angles
                #bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            else:
                add_pivot_rotation(obj, angle=euler_angles)
        
        #bpy.ops.object.select_all(action='SELECT')
        #bpy.context.view_layer.objects.active = active_object

        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected_objects:
            if obj:
                obj.select_set(True)
        
        
    def wrapper(*args, **kwargs):
        transformate_objects((-90.0, 0.0, 0.0))
        result = func(*args, **kwargs)
        transformate_objects((90.0, 0.0, 0.0))
        return result
    return wrapper
'''
#TODO: НЕОБХОДИМО ПОПРОБОВАТЬ ИСПРАВИТЬ РОДНОЙ КОД МЕТОДА bake_space_transform, ЧТОБЫ Apply Transform работала глубже первого дочернего объекта
def xd_edit_objects_decorator(func): # ПРОБА РЕАЛИЗАЦИИ ПОВОРОТА ВСЕХ ОБЪЕКТОВ СЦЕНЫ В МИРОВЫХ КООРДИНАТАХ

    
    def post_transformate_objects(rotation_matrix, objs_parent):
        # Поворачиваем все объекты в мировом пространстве
        # Угол поворота в радианах
        #angle = radians(90)
        
        # Поворот вокруг оси X
        #rotation_matrix = Matrix.Rotation(angle, 4, 'X')

        # Выносим все объекты в корень текущей коллекции
        for obj in bpy.data.objects:
            if obj.parent:
                obj.parent = None

        for obj in bpy.data.objects:
            #if obj.type == 'MESH':  # Применяем только к объектам типа "Меш"
            # Получаем текущую мировую матрицу объекта
            world_matrix = obj.matrix_world
            
            # Применяем вращение к мировой матрице
            new_world_matrix = rotation_matrix @ world_matrix
            
            # Устанавливаем новую мировую матрицу
            obj.matrix_world = new_world_matrix

        # Обновляем сцену, чтобы изменения отобразились
        bpy.context.view_layer.update()

        # Возвращаем все объекты своим родителям
        for obj, parent in objs_parent.items():
            if parent != None:
                bpy.data.objects[obj].parent = bpy.data.objects[parent]

        
    def wrapper(*args, **kwargs):
        import bmesh

        angle = radians(-90)
        rotation_matrix = Matrix.Rotation(angle, 4, 'X')
        rotation_matrix_rev = Matrix.Rotation(0, 4, 'X')
        
        # Выносим все объекты в корень текущей коллекции
        for obj in bpy.data.objects:
            obj_parent = obj.parent if obj.parent else None

            if not obj_parent:
                # world_matrix = obj.matrix_world
                # obj.matrix_world = rotation_matrix @ world_matrix
                # bm = bmesh.new()
                # bm.from_mesh(obj.data)
                # for v in bm.verts:
                #     v.co = rotation_matrix @ v.co
                # bm.to_mesh(obj.data)
                # bm.free()
                pass

            if obj_parent:
                # obj_rotation = obj.rotation_euler.copy()
                # rot_euler = (obj_rotation[0], obj_rotation[1], obj_rotation[2])
                # new_rot = (rot_euler[0] + angle, rot_euler[1], rot_euler[2])
                # obj.rotation_euler = new_rot


                # Поворачиваем текущий объект
                # world_matrix = obj.matrix_world
                # obj.matrix_world = rotation_matrix @ world_matrix
                pass

            # location = obj.matrix_world.translation.copy()
            # print(obj.name, location)
            
            # bm = bmesh.new()
            # bm.from_mesh(obj.data)
            # for v in bm.verts:
            #     v.co = rotation_matrix @ v.co
            # bm.to_mesh(obj.data)
            # bm.free()

            
            
            

        # Поворачиваем все объекты в мировом пространстве
        # for obj in bpy.data.objects:
        #     #if obj.type == 'MESH':  # Применяем только к объектам типа "Меш"
        #     # Получаем текущую мировую матрицу объекта
        #     world_matrix = obj.matrix_world
            
        #     # Применяем вращение к мировой матрице
        #     new_world_matrix = rotation_matrix @ world_matrix
            
        #     # Устанавливаем новую мировую матрицу
        #     obj.matrix_world = new_world_matrix
        
        # Возвращаем все объекты своим родителям
        # for obj, parent in objs_parent.items():
        #     if parent != None:
        #         world_location = bpy.data.objects[obj].matrix_world.translation
        #         bpy.data.objects[obj].parent = bpy.data.objects[parent]
        #         bpy.data.objects[obj].matrix_world.translation = world_location
        
        # Обновляем сцену, чтобы изменения отобразились
        # bpy.context.view_layer.update()
        
        result = func(*args, **kwargs)

        #angle = radians(90)
        #rotation_matrix = Matrix.Rotation(angle, 4, 'X')
        #post_transformate_objects(rotation_matrix, objs_parent)
        return result
    return wrapper