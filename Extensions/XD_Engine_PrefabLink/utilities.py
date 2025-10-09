import bpy

def init_search_mode():
    bpy.context.scene.xdpl_attributes.search_mode = False
    
    selected_objects = bpy.context.selected_objects
    if len(selected_objects) == 0:
        bpy.context.scene.xdpl_attributes.search_mode = True

def get_active_object(): # определяем активный объект
    a_object = bpy.context.view_layer.objects.active
    if a_object is None: # если нет то назначаем активным первый попавшийся
        a_object = bpy.data.objects[0]
        bpy.context.view_layer.objects.active = a_object
    return a_object

def is_no_objects(): # есть ли в сцене объекты
    if len(bpy.data.objects) == 0: return True
    return False

def debug_log(*args, enable=False):
    """
    Вывод дебага в консоль.
    """
    if not enable: return
    print(" ".join(args))