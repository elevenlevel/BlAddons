from calendar import c
import bpy
from bpy.types import Context, Operator
from .utils.functions import *
from .utils.bakers import *
import subprocess
import os

class XD_Open_Folder(Operator):
    # открываем папку с готовыми текстурами
    bl_idname = "scene.open_folder_op"
    bl_label = "Open Folder"
    bl_description = "BakOpen Current Folder in Explorer" 
    bl_options = {'REGISTER'}

    def execute(self, context):
        dir_path = context.scene.xd_baker.attributes.bake_folder
        abspath = bpy.path.abspath(dir_path)
        
        # проверяем, существует ли папка
        if not os.path.exists(abspath):
            return {'FINISHED'}
        
        subprocess.Popen(f'explorer "{abspath}"')
        return {'FINISHED'}


class XD_Apply_Cage_Modifiers(Operator):
    bl_idname = "object.apply_cage_modifiers"
    bl_label = "Apply Cage Modifiers"
    bl_description = "The use of all available modifiers on objects" 
    bl_options = {'REGISTER'}

    def execute(self, context):
        # Создаем временную копию объекта
        context.scene.xd_baker.attributes.apply_modifiers = not context.scene.xd_baker.attributes.apply_modifiers
        scene = context.scene
        
        if scene.xd_baker.attributes.apply_modifiers: # когда чекбокс включается
            backup_objects_selection() # собираем данные о выделении всех объектов в сцене

            # собираем в словарь данные о том, в каких коллекциях лежат объекты
            collections_dict = {}
            for collection in bpy.data.collections:
                for obj in collection.objects:
                    collections_dict[obj.name] = collection.name

            for obj in bpy.data.objects: # чистим сцену от старых gpy кейджей
                obj.select_set(False) # параллельно снимаем выделение со всех объектов

                if "#gpu#cage" in obj.name or "#gpu#mask" in obj.name:
                    bpy.data.objects.remove(obj)
                
            if scene.xd_baker.attributes.bake_type == 'OBJECTS': # OBJECT BAKE TYPE
                objects = [scene.xd_baker.attributes.low_poly_obj, scene.xd_baker.attributes.high_poly_obj]
                
                for obj in objects:
                    if len(obj.modifiers) > 0:
                        cage_object = obj.copy()
                        cage_object.data = obj.data.copy()
                        
                        if obj.name == scene.xd_baker.attributes.low_poly_obj.name:
                            cage_object.name = obj.name + "#gpu#cage"
                        elif obj.name == scene.xd_baker.attributes.high_poly_obj.name:
                            cage_object.name = obj.name + "#gpu#mask"
                        
                        obj_collection = bpy.data.collections[collections_dict[obj.name]] # коллекция с текущим объектом
                        obj_collection.objects.link(cage_object)
                        bpy.context.view_layer.objects.active = cage_object
                        
                        for modifier in cage_object.modifiers:
                            bpy.ops.object.modifier_apply(modifier=modifier.name)
                        obj_collection.objects.unlink(cage_object)
            
            elif scene.xd_baker.attributes.bake_type == 'COLLECTIONS': # COLLECTIONS BAKE TYPE
                for collection in scene.xd_baker.attributes.my_collection.group:
                    if collection.name == "": continue
                    real_collection = bpy.data.collections[collection.name]
                    
                    for obj in  real_collection.objects:
                        if len(obj.modifiers) > 0:
                            if obj.name.lower().endswith("_low"):
                                cage_object = obj.copy()
                                cage_object.data = obj.data.copy()
                                cage_object.name = obj.name + "#gpu#cage"
                                real_collection.objects.link(cage_object)
                                bpy.context.view_layer.objects.active = cage_object
                                
                                # применяем модификаторы к временным объектам на которых модификаторы есть
                                for modifier in cage_object.modifiers:
                                    bpy.ops.object.modifier_apply(modifier=modifier.name)
                                real_collection.objects.unlink(cage_object)
                            elif obj.name.lower().endswith("_high"):
                                cage_object = obj.copy()
                                cage_object.data = obj.data.copy()
                                cage_object.name = obj.name + "#gpu#mask"
                                real_collection.objects.link(cage_object)
                                bpy.context.view_layer.objects.active = cage_object
                                
                                # применяем модификаторы к временным объектам на которых модификаторы есть
                                for modifier in cage_object.modifiers:
                                    bpy.ops.object.modifier_apply(modifier=modifier.name)
                                real_collection.objects.unlink(cage_object)
            
            restore_objects_selection() # восстанавливаем выделение объектов
        else:
            for obj in bpy.data.objects:
                if obj.name.endswith("#gpu#cage") or obj.name.endswith("#gpu#mask"):
                    bpy.data.objects.remove(obj)
        
        
        return {'FINISHED'}


class XD_Bake_Op(Operator):
    bl_idname = "object.bake_op"
    bl_label = "Bake maps"
    bl_description = "Bake image maps for low and high poly objects" 
    bl_options = {'REGISTER'}

    # def __init__(self):
    #     pass

    def select_and_bake_map(self, context, map_name):
        if map_name == 'Diffuse':
            bake_diffuse_map(context, map_name)
        if map_name == 'AO':
            bake_ao_map(context, map_name)
        if map_name == 'Normal':
            bake_normal_map(context, map_name)
        if map_name == 'Normal os':
            bake_normal_os_map(context, map_name)
        if map_name == 'Position':
            bake_position_map(context, map_name)
        if map_name == 'Roughness':
            bake_roughness_map(context, map_name)
        if map_name == 'Emission':
            bake_emission_map(context, map_name)
        if map_name == 'Curvature':
            bake_curvature_map(context, map_name)
        if map_name == 'Edge Wear':
            bake_edge_wear_map(context, map_name)
        if map_name == 'Vertex Color':
            bake_vertex_color_map(context, map_name)
        if map_name == 'Height':
            bake_height_map(context, map_name)
        if map_name == 'Opacity':
            bake_opacity_map(context, map_name)
        if map_name == 'Custom':
            bake_custom_map(context, map_name)
        if map_name == 'UV Wire':
            bake_uv_wire_map(context, map_name)

    def start_baking(self, context, collection = None):
        bake_maps_group = context.scene.xd_baker.attributes.bake_maps_group.maps_group

        for iter in bake_maps_group:
            map_name = iter.name
            map_unfolded = iter.unfolded
            map_enabled = iter.enabled
            map_colorspace = iter.colorspace
            map_alpha = iter.alpha
            map_depth = iter.depth
            map_options = iter.options
            
            if map_enabled:
                backup_objects_render_state() # собираем данные о скрытии всех объектов в сцене
                backup_objects_selection() # собираем данные о выделении всех объектов в сцене
                
                try:
                    combine_meshes(context, collection, map_name)
                    create_cage_object(context)
                    select_prebaked_objects(context)
                    create_img_node(map_name, map_colorspace, map_alpha)
                    self.select_and_bake_map(context, map_name)
                    
                    if map_name != 'UV Wire':
                        caching_image(context)
                        filtering_image(context, map_name, map_depth)
                        if context.scene.xd_baker.attributes.enable_save:
                            save_texture(context, collection, map_depth)
                except:
                    pass
                finally:
                    clear_template_things(context)
                    restore_objects_render_state() # восстанавливаем отображение всех объектов
                    restore_objects_selection() # восстанавливаем выделение всех объектов

    def execute(self, context):
        # проверка если сцена сохранена
        if context.scene.xd_baker.attributes.enable_save:
            if not bpy.data.is_saved:
                self.report({'ERROR'}, "Scene is not saved! Please save scene. CANCELLED")
                return {'CANCELLED'}

        start_time = start_timer()

        context.scene.xd_baker.attributes.is_baking = True
        scene = context.scene

        
        # запоминаем старые параметры рендера
        old_engine = bpy.context.scene.render.engine
        bpy.context.scene.xd_baker.backup.old_engine = old_engine

        if old_engine == 'CYCLES': # переключаем device на GPU, если рендер CYCLES
            bpy.context.scene.xd_baker.backup.old_device = bpy.context.scene.cycles.device
            bpy.context.scene.cycles.device = "GPU"
        
        else: # переключаем рендер на cycles
            bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.xd_baker.backup.old_device = bpy.context.scene.cycles.device
            bpy.context.scene.cycles.device = "GPU"


        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        if context.scene.xd_baker.attributes.bake_type == 'OBJECTS': # режим запечения объектов
            self.start_baking(context)
        elif context.scene.xd_baker.attributes.bake_type == 'COLLECTIONS': # режим запечения коллекций
            my_collections = scene.xd_baker.attributes.my_collection.group
            
            # определяем включенные/выключенные коллекции
            layer_collection = bpy.context.layer_collection
            get_excluded_collections(layer_collection, my_collections)
            
            for single_collection in my_collections:
                if single_collection.name == '':
                    # попадаются странные коллекции без имени
                    continue
                
                if 'excluded' in single_collection and single_collection['excluded'] == True:
                    # если коллекция выключена, то пропускаем итерацию
                    continue
                
                self.start_baking(context, single_collection)
                
        # восстанавливаем старые значения параметров рендера
        bpy.context.scene.render.engine = bpy.context.scene.xd_baker.backup.old_engine
        bpy.context.scene.cycles.device = bpy.context.scene.xd_baker.backup.old_device
        context.scene.xd_baker.attributes.is_baking = False
        
        end_timer(self, start_time)
        return {'FINISHED'}


class XD_RemColList_Op(Operator):
    # удаление коллекции из списка коллекций бейкера
    bl_idname = "my.remove_item"
    bl_label = "Remove Collection"
    bl_description = "Add or Remove a collection from the list" 
    bl_options = {'REGISTER'}

    index: bpy.props.IntProperty() # type: ignore

    def execute(self, context):
        scene = context.scene
        my_collection = scene.xd_baker.attributes.my_collection
        group = my_collection.group
        
        for i, item in enumerate(group):
            if item.index == self.index:
                my_collection.group.remove(i)
                break
        
        update_desgraph()
        return {'FINISHED'}


class XD_OT_About_XDBaker(Operator):
    bl_idname = "wm.about_xdbaker"
    bl_label = "About XD Baker"
    bl_description = "About XD Baker"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=200)
    def draw(self, context):
        layout = self.layout
        layout.label(text = "XD Baker")
        layout.label(text = "Version: 0.1.0")
        layout.label(text = "Autor: Roman Askarov")
        layout.label(text = "https://example.com") # TODO: нужно отрисовать как кнопку
    def execute(self, context):
        return {'FINISHED'}