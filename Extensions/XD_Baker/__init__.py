import bpy
from bpy.props import *
from bpy.app.handlers import persistent
from . xd_baker_panel import *
from . xd_baker_operators import *
from .utils.functions import draw_low_gpu_cage, draw_high_gpu_cage
from .addon_data import XDBaker, data_classes, bake_maps_list

def update():
    def update_assign_objects():
        xd_baker = bpy.context.scene.xd_baker
        bake_type = xd_baker.attributes.bake_type
        all_objects = bpy.context.view_layer.objects
    
        if bake_type == "OBJECTS":
            high_poly_obj = xd_baker.attributes.high_poly_obj
            low_poly_obj = xd_baker.attributes.low_poly_obj
            
            if high_poly_obj is not None and not high_poly_obj.name in all_objects:
                xd_baker.attributes.high_poly_obj = None
            if low_poly_obj is not None and not low_poly_obj.name in all_objects:
                xd_baker.attributes.low_poly_obj = None
            
        elif bake_type == "COLLECTIONS":
            pass

    def get_issues(xd_baker): # проверка на наличие проблем
        bake_type = xd_baker.attributes.bake_type
        low_poly_obj = xd_baker.attributes.low_poly_obj
        high_poly_obj = xd_baker.attributes.high_poly_obj

        xd_baker.alert_ui.low_poly_obj_ui = False
        xd_baker.alert_ui.high_poly_obj_ui = False
        xd_baker.alert_ui.bake_maps_button_ui = False

        if get_selected_maps_cnt(bpy.context) == 0: # если ни одна карта не выбрана
            xd_baker.alert_ui.bake_maps_button_ui = True
        
        if bake_type == 'OBJECTS':
            if low_poly_obj == None: # если low_poly_obj не указан
                xd_baker.alert_ui.low_poly_obj_ui = True
                xd_baker.alert_ui.bake_maps_button_ui = True

            else:
                if len(low_poly_obj.data.uv_layers) == 0: # если low_poly_obj без uv
                    xd_baker.alert_ui.bake_maps_button_ui = True
            
            if high_poly_obj == None: # если high_poly_obj не указан
                xd_baker.alert_ui.high_poly_obj_ui = True
                xd_baker.alert_ui.bake_maps_button_ui = True
        
        elif bake_type == 'COLLECTIONS':
            if xd_baker.attributes.my_collection.group[0].name == "": # если не указано ни одной коллекции
                xd_baker.alert_ui.bake_maps_button_ui = True

    xd_baker = bpy.context.scene.xd_baker
    get_issues(xd_baker)
    update_assign_objects()

@persistent 
def initialize_addon(scene): # инициализация аддона
    update()

    scene = bpy.context.scene
    mycollection = scene.xd_baker.attributes.my_collection

    # если коллекция пустая, то добавляем один элемент
    if len(mycollection.group)==0:
        item = mycollection.group.add()
        item.name = ""
        item.index = 0

    temp_things = scene.xd_baker.attributes.bake_maps_group
    
    if str(bake_maps_list) != scene.xd_baker.backup.old_bake_maps_list: # если список параметров аддона изменился
        scene.xd_baker.backup.old_bake_maps_list = str(bake_maps_list) # сохраняем список параметров аддона
        temp_things.maps_group.clear()  # очищаем список maps_group
        
        for map_name, map_items in bake_maps_list.items():
            addon_item = temp_things.maps_group.add()
            addon_item.name = map_name
            addon_item.unfolded = map_items["unfolded"]
            addon_item.enabled = map_items["enabled"]
            addon_item.colorspace = map_items["colorspace"]
            addon_item.alpha = map_items["alpha"]
            addon_item.depth = map_items["depth"]

            for opt_name, opt_items in map_items["options"].items():
                opt_item = addon_item.options.add()
                opt_item.name = opt_name
                opt_item.type = opt_items["type"]
                
                if opt_items["type"] == "ENUM": # ЭТО СЕЙЧАС НЕ РАБОТАЕТ ИЗ-ЗА СЛОЖНОСТИ С ЗАПОЛНЕНИЕМ EnumProperty ЗНАЧЕНИЯМИ ИЗ СПИСКА bake_maps_list
                    #value = r'("Expanded","Expanded","_"), ("Shrinked","Shrinked","_")'
                    #print(opt_items["value"])
                    #setattr(opt_item, "enum_value", value)
                    for v in opt_items["value"]:
                        opt_item.enum_value = v[0]
                        
                else:
                    setattr(opt_item, opt_items["type"].lower() + "_value", opt_items["value"])
    
    # удаляем подготовленные заранее кейджи, если они есть
    for obj in bpy.data.objects:
        if obj.name.endswith("#gpu#cage") or obj.name.endswith("#gpu#mask"):
            bpy.data.objects.remove(obj)
    scene.xd_baker.attributes.apply_modifiers = False

@persistent 
def update_addon(scene):
    update()

classes = (
    *data_classes,
    XD_RemColList_Op,
    XD_Bake_Op,
    XD_Open_Folder,
    XD_OT_About_XDBaker,
    XD_Apply_Cage_Modifiers,
    XD_PT_Panel,
    XD_PT_Images_Panel,
    XD_PT_Cage_Panel,
    # XD_PT_Settings_Panel,
    )

# глобальные переменные для хранения состаяния кейджа
low_cage = None
high_cage = None


def register():
    for c in classes:
        bpy.utils.register_class(c)
    
    global low_cage
    global high_cage
    bpy.types.Scene.xd_baker = bpy.props.PointerProperty(type=XDBaker)
    bpy.app.handlers.load_post.append(initialize_addon)
    bpy.app.handlers.depsgraph_update_post.append(update_addon)

    low_cage = bpy.types.SpaceView3D.draw_handler_add(draw_low_gpu_cage, (), 'WINDOW', 'POST_VIEW')
    high_cage = bpy.types.SpaceView3D.draw_handler_add(draw_high_gpu_cage, (), 'WINDOW', 'POST_VIEW')

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

    global low_cage
    global high_cage
    if low_cage is not None:
        bpy.types.SpaceView3D.draw_handler_remove(low_cage, 'WINDOW')
        low_cage = None
    if high_cage is not None:
        bpy.types.SpaceView3D.draw_handler_remove(high_cage, 'WINDOW')
        high_cage = None
    
    bpy.app.handlers.depsgraph_update_post.remove(update_addon)
    bpy.app.handlers.load_post.remove(initialize_addon)
    del bpy.types.Scene.xd_baker

if __name__ == "__main__":
    register()