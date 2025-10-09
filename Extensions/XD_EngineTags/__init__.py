# TODO: нарисовать иконку с прочерком в квадратике DONE
# TODO: если у объектов разные теги, то НЕ блокировать список, а менять состояние чекбокса на прочерк в квадратике DONE
# TODO: кнопка Clear Objects не должна быть скрыта когда выбрано несколько объектов DONE
# TODO: кнопку Clear Objects необходимо переименовать в Clear Tags DONE

'''
    @Author: Roman Askarov
    @version: 25.11.2024
    @description: Плагин для работы с тегами в Blender
    @license: XDevs Internal License
'''

from .tags import default_tags
import bpy
from .utilities import *
from .panels import *
from bpy.app.handlers import persistent

previous_user_tags = []
previous_act_object = None
previous_sel_objects = []


class UserTagsItem(bpy.types.PropertyGroup):
    """Тег пользовательского списка"""
    name : bpy.props.StringProperty(name="Tag Name") # type: ignore
    state : bpy.props.StringProperty(default="True") # type: ignore
    exists : bpy.props.BoolProperty(default=True) # type: ignore


class MegaTagsItem(bpy.types.PropertyGroup):
    """Тег списка режима mega_mode"""
    name : bpy.props.StringProperty(name="Tag Name") # type: ignore
    state : bpy.props.StringProperty(default="False") # type: ignore
    exists : bpy.props.BoolProperty(default=True) # type: ignore


class PrefabLinks(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(name="Prefab Link") # type: ignore


class XDET_Attributes(bpy.types.PropertyGroup):
    """Основные атрибуты аддона"""
    user_tags : bpy.props.CollectionProperty(type=UserTagsItem) # type: ignore # кастомные теги пользователя
    mega_tags : bpy.props.CollectionProperty(type=MegaTagsItem) # type: ignore
    prefab_links : bpy.props.CollectionProperty(type=PrefabLinks) # type: ignore
    property_tags : bpy.props.StringProperty(name="Property Tags", default=default_tags) # type: ignore
    tags_string : bpy.props.StringProperty() # type: ignore
    property_name : bpy.props.StringProperty(default="Tags") # type: ignore # позже нужно использовать это вместо "Tags"

    user_tags_index : bpy.props.IntProperty(default=-1) # type: ignore

    show_panels : bpy.props.BoolProperty(default=True) # type: ignore
    a_object : bpy.props.PointerProperty(type=bpy.types.Object) # type: ignore
    selected_is_similar : bpy.props.BoolProperty(default=False) # type: ignore

    show_advanced : bpy.props.BoolProperty(default=False) # type: ignore
    mark_property_tags : bpy.props.BoolProperty(default=True) # type: ignore
    mega_mode : bpy.props.BoolProperty(default=False) # type: ignore


@persistent
def pre_expand_tags(dummy):
    """Инициализация аддона в сцене"""
    debug_log("Info:", "PreExpandTags")
    global previous_user_tags
    global previous_act_object
    global previous_sel_objects

    xdet_attributes = bpy.context.scene.xdet_attributes
    user_tags = xdet_attributes.user_tags # теги сохраненные в сцене
    all_objects = bpy.data.objects
    active_object = bpy.context.view_layer.objects.active
    
    # сохраняем текущие данные для дальнейшего сравнения
    if user_tags is not None:
        clean_attrib_spaces(xdet_attributes.user_tags)
        previous_user_tags = [x.name for x in user_tags]
    previous_act_object = bpy.context.view_layer.objects.active
    previous_sel_objects = bpy.context.selected_objects

    get_show_panel()

    if all_objects is not None: # если в сцене вообще есть объекты
        def recombine_user_tags(all_tags_list, active_object_tags_list):
            """
            Заново заполняем user_tags и свойства его айтемов.
            """
            selected_objects = bpy.context.selected_objects
            xdet_attributes = bpy.context.scene.xdet_attributes

            if len(xdet_attributes.user_tags) != 0: # если в сцене уже есть user_tags
                clean_attrib_spaces(xdet_attributes.user_tags) # чистим user_tags от пустых элементов
                
                # сначала добавляем к user_tags теги с объектов сцены
                for tag in all_tags_list:
                    if tag not in user_tags:
                        new_tag = user_tags.add()
                        new_tag.name = tag.strip()
                        
                # устанавливаем состояние стрелочек и состояние чекбоксов
                for tag in user_tags:
                    tag.exists = tag.name in all_tags_list
                    if len(selected_objects) < 2:
                        tag.state = str(tag.name in active_object_tags_list)
                    elif len(selected_objects) > 1:
                        all_tags_list, common_tags_list, unical_tags_list = split_common_unical_tags(selected_objects, user_tags)
                        
                        if tag.name in common_tags_list:
                            tag.state = "True"
                        elif tag.name in unical_tags_list:
                            tag.state = "Partly"
                        else:
                            tag.state = "False"
                            
                property_tags_list = list(x.strip() for x in xdet_attributes.property_tags.split(","))
                xdet_attributes.property_tags = ",".join(property_tags_list)
                
            elif len(user_tags) == 0: # если в сцене еще нет user_tags
                # заполняем чистый user_tags
                xdet_attributes.user_tags.clear() # чтобы было
                property_tags_list = list(x.strip() for x in xdet_attributes.property_tags.split(","))
                
                # заполняем user_tags всеми тегами
                for tag in property_tags_list:
                    new_tag = xdet_attributes.user_tags.add()
                    new_tag.name = tag.strip()
                    new_tag.state = "False"
                    new_tag.exists = tag in all_tags_list
                
                xdet_attributes.property_tags = ",".join(property_tags_list)
            xdet_attributes.tags_string = ",".join(all_tags_list)
        
        all_scene_objects_tags = collect_objects_tags(all_objects)
        active_object_tags_list = collect_objects_tags(bpy.context.selected_objects)
        recombine_user_tags(all_scene_objects_tags, active_object_tags_list) # _collect_objects_tags возвращает all_tags_list
        get_prefab_links()
    
    elif all_objects is None: # если сцена без объектов
        xdet_attributes.user_tags.clear()
        
        for tag in default_tags.split(","):
            new_tag = xdet_attributes.user_tags.add()
            new_tag.name = tag
            new_tag.state = "False"
            new_tag.exists = False
            
        xdet_attributes.tags_string = ",".join(default_tags.split(","))
        
    add_last_empty_tag()
    rewrite_mega_tags(user_tags)


@persistent
def update_tags_by_select(scene):
    """Обновление состояния аддона при выборе другого объекта"""
    debug_log("Info:", "UpdateTagsBySelect")

    def _update_single(object, xdet_attributes):
            if bpy.context.scene.xdet_attributes.mega_mode:
                return
            user_tags = xdet_attributes.user_tags
            clean_attrib_spaces(xdet_attributes.user_tags)
            
            if object.get("Tags") is not None:
                obj_tags_list = object.get("Tags").split(",")
                obj_tags_list = clean_list(obj_tags_list) # чистим от пустых элементов

                # включаем чекбоксы, если теги есть в объекте
                for u_tag in user_tags:
                    u_tag.state = str(u_tag.name in obj_tags_list)

                # добавляем в интерфейс незнакомые теги
                for o_tag in obj_tags_list:
                    if o_tag.strip() not in user_tags:
                        new_tag = user_tags.add()
                        new_tag.name = o_tag.strip()
                        new_tag.state = "False"
                
                #user_tags_list = []
                #for u_tag in user_tags:
                #    if u_tag.state == "True":
                #        user_tags_list.append(u_tag.name)
            else:
                for tag in user_tags:
                    tag.state = "False"
            
            # обновляем состояние стрелочек
            for u_tag in user_tags:
                u_tag.exists = u_tag.name in collect_objects_tags(bpy.data.objects)
            #for x in user_tags: print(x.name)
    def _update_multiple(objects, xdet_attributes):
        if bpy.context.scene.xdet_attributes.mega_mode:
            return
        user_tags = xdet_attributes.user_tags
        clean_attrib_spaces(xdet_attributes.user_tags)

        all_tags_list, common_tags_list, unical_tags_list = split_common_unical_tags(objects, user_tags)
        
        # добавляем в интерфейс незнакомые теги
        for o_tag in all_tags_list:
            if o_tag not in user_tags:
                new_tag = user_tags.add()
                new_tag.name = o_tag
                new_tag.state = "False"
                
        # устанавливаем состояние чекбоксов
        for u_tag in user_tags:
            if u_tag.name in all_tags_list:
                u_tag.state = "True"
            else:
                u_tag.state = "False"
                
            # обновляем состояние стрелочек
            for u_tag in user_tags:
                u_tag.exists = u_tag.name in collect_objects_tags(bpy.data.objects)
        
        for u_tag in user_tags:
            if u_tag.name in unical_tags_list:
                u_tag.state = "Partly"
                
    xdet_attributes = bpy.context.scene.xdet_attributes
    user_tags = xdet_attributes.user_tags
    
    selected_objects = bpy.context.selected_objects
    active_object = bpy.context.view_layer.objects.active

    global previous_user_tags
    global previous_act_object
    global previous_sel_objects
    
    get_show_panel()
    
    if len(selected_objects) < 2:
        if active_object:
            _update_single(active_object, xdet_attributes)
        else:
            return
    elif len(selected_objects) > 1:
        debug_log("check_similar:", check_similar(selected_objects))
        if check_similar(selected_objects):
            for object in selected_objects:
                _update_single(object, xdet_attributes)
        else:
            _update_multiple(selected_objects, xdet_attributes)
    
    if bpy.context.scene.xdet_attributes.mega_mode:
        rewrite_mega_tags(user_tags)
    
    previous_user_tags = [x.name for x in user_tags]
    previous_act_object = active_object
    previous_sel_objects = selected_objects
    add_last_empty_tag()
    get_prefab_links()

class UpdateUserTags(bpy.types.Operator): ### при активации тега  не обновляется индикатор (стрелка) наличия тега в сцене
    """Обновляем атрибут с тегами при изменении чекбокса"""
    bl_idname = "scene.update_user_tags"
    bl_label = "Update User Tags"
    bl_description = ""
    #bl_options = {'REGISTER', 'INTERNAL'}
    
    tag_name : bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        debug_log("UpdateUserTags")

        xdet_attributes = bpy.context.scene.xdet_attributes
        user_tags = xdet_attributes.user_tags
        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.view_layer.objects.active
        
        if bpy.context.scene.xdet_attributes.mega_mode:
            mega_tags = xdet_attributes.mega_tags
            current_tag = mega_tags.get(self.tag_name)
            current_tag.state = "True" if current_tag.state == "False" or current_tag.state == "Partly" else "False"
            return {'FINISHED'}

        # берем тег из атрибута по текущему имени
        current_tag = user_tags.get(self.tag_name)
        # переключаем чекбокс по нажатию
        tag_state_before = current_tag.state
        current_tag.state = "True" if current_tag.state == "False" or current_tag.state == "Partly" else "False"

        if selected_objects is None:
            return {'FINISHED'}
        
        for object in selected_objects:
            if object.get("Tags") is None:
                all_tags_list = []
                all_tags_list.append(current_tag.name)
                xdet_attributes.tags_string = ",".join(all_tags_list)
            elif object.get("Tags") is not None:
                obj_tags_str = object.get("Tags")
                obj_tags_list = obj_tags_str.split(",")
                obj_tags_list = clean_list(obj_tags_list) # чистим от пустых элементов
                
                # добавляем или убираем тег из obj_tags_list в зависимости от состяния чекбокса
                if current_tag.name in obj_tags_list:
                    if current_tag.state == "Partly":
                        pass
                    elif current_tag.state == "False":
                        obj_tags_list.remove(current_tag.name)
                    else:
                        obj_tags_list.append(current_tag.name)
                else:
                    if current_tag.state == "Partly":
                        pass
                    elif current_tag.state == "True":
                        obj_tags_list.append(current_tag.name)
                    else:
                        obj_tags_list.remove(current_tag.name)
            
                obj_tags_list = clean_list(obj_tags_list) # убераем пустые элементы

                # конвертирвем список в строку
                xdet_attributes.tags_string = ",".join(obj_tags_list)
        
            # записываем строку в объекты в качестве тега
            write_tags_to_object(object)
            add_last_empty_tag()
        update_exist()
        return {'FINISHED'}


class AddUserTag(bpy.types.Operator):
    #Добавляем новый пользовательский тег
    bl_idname = "scene.add_user_tag"
    bl_label = "Add User Tags"
    bl_description = "Add new tag"
    #bl_options = {'REGISTER', 'INTERNAL'}
    
    tag_name : bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        xdet_attributes = bpy.context.scene.xdet_attributes
        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.view_layer.objects.active
        user_tags = xdet_attributes.user_tags

        if self.tag_name == "":
            return {'FINISHED'}
        debug_log("AddUserTag")

        tag_name = fix_non_latin(self, self.tag_name)

        # читаем теги активного объекта (если есть) и преобразуем в список
        if active_object.get("Tags") is not None:
            obj_tags_str = active_object.get("Tags")
            obj_tags_list = obj_tags_str.split(",")
            if tag_name in obj_tags_list:
                return {'FINISHED'}
            obj_tags_list.append(tag_name) # добавляем новый элемент в список
            obj_tags_list = clean_list(obj_tags_list) # чистим от пустых элементов
            
            # редактируем последний тег
            new_tag = user_tags.add()
            new_tag.name = tag_name
            new_tag.state = "True"
            new_tag.exists = True

            # преобразование списка тегов в строку
            xdet_attributes.tags_string = ",".join(obj_tags_list)
        else:
            # дополняем список пользовательских тегов
            new_tag = user_tags.add()
            new_tag.name = tag_name
            new_tag.state = "True"
            new_tag.exists = True
            xdet_attributes.tags_string = tag_name

        if len(selected_objects) < 2:
            write_tags_to_object(active_object)
        else:
            for object in selected_objects:
                write_tags_to_object(object)
        
        add_last_empty_tag()
        rewrite_mega_tags(user_tags)
        return {'FINISHED'}


class RemoveUserTag(bpy.types.Operator):
    """Удаляем пользовательский тег"""
    bl_idname = "scene.remove_user_tag"
    bl_label = "Remove Tag"
    bl_description = "Remove tag"
    #bl_options = {'REGISTER', 'INTERNAL'}
    
    tag_name : bpy.props.StringProperty() # type: ignore
    
    def execute(self, context):
        debug_log("RemoveUserTag")
        tag_name = self.tag_name.strip()
        xdet_attributes = bpy.context.scene.xdet_attributes
        user_tags = xdet_attributes.user_tags
        all_scene_objects = bpy.data.objects
        
        # удаляем тег из user_tags
        for i, tag in enumerate(user_tags):
            if tag.name == tag_name:
                xdet_attributes.user_tags.remove(i)

        for object in all_scene_objects:
            object_tags = object.get("Tags")
            if object_tags is None: continue
            obj_tags_list = object_tags.split(",")
            obj_tags_list = clean_list(obj_tags_list)

            if tag_name in obj_tags_list:
                obj_tags_list.remove(tag_name)
                xdet_attributes.tags_string = ",".join(obj_tags_list)
                write_tags_to_object(object)
        
        return {'FINISHED'}


class SelectSimilar(bpy.types.Operator):
    """Выделяем объекты с аналогичными тегами"""
    bl_idname = "scene.select_similar"
    bl_label = "Select Similar"
    bl_description = "Select all objects with similar tags"
    #bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        debug_log("SelectSimilar")

        if bpy.context.scene.xdet_attributes.mega_mode: 
            search_tags = bpy.context.scene.xdet_attributes.mega_tags
        else:
            search_tags = bpy.context.scene.xdet_attributes.user_tags

        search_tags_list = []
        searched_objects = []

        for tag in search_tags:
            if tag.state == "True" and tag.name != "":
                search_tags_list.append(tag.name)
        
        for obj in bpy.data.objects:
            if obj.get("Tags") is None:
                continue
            
            # теги объекта текущей итерации
            item_obj_tags = obj.get("Tags").split(",")

            # сравнение тегов текущего объекта с тегами объекта текущей итерации
            if sorted(set(item_obj_tags)) == sorted(set(search_tags_list)):
                searched_objects.append(obj.name)
        
        if len(searched_objects) > 0:
            # назначаем активным первый из списка
            bpy.context.view_layer.objects.active = bpy.data.objects[searched_objects[0]]
            # сбрасываем выделение всех объектов
            for obj in bpy.data.objects:
                if obj.name in searched_objects:
                    obj.select_set(True)
                else:
                    obj.select_set(False)
        
        return {'FINISHED'}


class RestoreDefault(bpy.types.Operator):
    """Выделяем объекты с аналогичными тегами"""
    bl_idname = "scene.restore_default"
    bl_label = "Restore Default"
    bl_description = "Restore Default"
    #bl_options = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        debug_log("RestoreDefault")

        xdet_attributes = bpy.context.scene.xdet_attributes
        user_tags = xdet_attributes.user_tags
        all_scene_objects = bpy.data.objects
        active_object = bpy.context.view_layer.objects.active
        objects_tags_list = collect_objects_tags(all_scene_objects)
        
        # сохраняем состояние тегов
        old_tags = {}
        for tag in user_tags:
            old_tags[tag.name] = tag.state
        
        # собираем список всех тегов сцены и соединяем с тегами из настроек аддона
        property_tags_list = []
        property_tags_list = list(x.strip() for x in xdet_attributes.property_tags.split(","))
        objects_tags_list = list(set(objects_tags_list) - set(property_tags_list))
        all_tags_list = property_tags_list + objects_tags_list
        all_tags_list = list(sorted(set(all_tags_list)))
        user_tags.clear()
        
        # добавляем теги по умолчанию
        for tag in all_tags_list:
            new_tag = user_tags.add()
            new_tag.name = tag.strip()
            if tag.strip() in old_tags:
                new_tag.state = old_tags[tag.strip()]
            else:
                new_tag.state = "False"
            new_tag.exists = tag in objects_tags_list
        
        add_last_empty_tag()
        return {'FINISHED'}


class SetDefaultParms(bpy.types.Operator):
    bl_idname = "scene.set_default_parms"
    bl_label = "Reset"
    bl_description = "Press to set Default Parameters"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        debug_log("SetDefaultParms")
        xdet_attributes = bpy.context.scene.xdet_attributes
        xdet_attributes.property_tags = default_tags
        return {'FINISHED'}


class SelectLikeThis(bpy.types.Operator):
    """Выделяем объекты с этим тегом"""
    bl_idname = "scene.select_like_this"
    bl_label = "Select Like This"
    bl_description = "Select all objects with this tag"
    #bl_options = {'REGISTER', 'INTERNAL'}
    
    tag_name : bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        debug_log("SelectLikeThis")
        tag_name = self.tag_name
        selected_objects = []

        all_objects = bpy.data.objects
        for obj in all_objects:
            if obj.get("Tags") is None:
                continue

            if tag_name in obj.get("Tags").split(","):
                selected_objects.append(obj)
        
        if len(selected_objects) > 0:
            # назначаем активным первый из списка
            bpy.context.view_layer.objects.active = selected_objects[0]
            # выделяем объекты
            for obj in bpy.data.objects:
                if obj in selected_objects:
                    obj.select_set(True)
                else:
                    obj.select_set(False)
        
        return {'FINISHED'}


class ClearTags(bpy.types.Operator):
    """Удаление тегов с выбранных объектов"""
    bl_idname = "scene.clear_tags"
    bl_label = "Clear Tags"
    bl_description = "Remove Tags attribute from selected objects"
    #bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        debug_log("ClearObjects")
        selected_objects = bpy.context.selected_objects
        xdet_attributes = bpy.context.scene.xdet_attributes
        user_tags = xdet_attributes.user_tags
        mega_tags = xdet_attributes.mega_tags

        for object in selected_objects:
            if object.get("Tags") is not None:
                xdet_attributes.tags_string = ""
                write_tags_to_object(object)
        
        all_scene_objects_tags = collect_objects_tags(bpy.data.objects)

        for tag in user_tags:
            tag.state = "False"
            tag.exists = tag.name in all_scene_objects_tags
        for tag in mega_tags:
            tag.exists = tag.name in all_scene_objects_tags
        
        return {'FINISHED'}


class ClearAllObjects(bpy.types.Operator):
    """Удаление тегов со всех объектов и из сцены"""
    bl_idname = "scene.clear_all_objects"
    bl_label = "Clear All Objects"
    bl_description = "Remove Tags attribute from all objects"
    bl_options = {'REGISTER', 'INTERNAL'}

    objects_only : bpy.props.BoolProperty(default=True) # type: ignore

    def execute(self, context):
        debug_log("ClearAllObjects")
        all_objects = bpy.data.objects
        xdet_attributes = bpy.context.scene.xdet_attributes

        for object in all_objects:
            if object.get("Tags") is not None:
                xdet_attributes.tags_string = ""
                write_tags_to_object(object)
        
        for tag in xdet_attributes.user_tags:
            tag.state = "False"
            tag.exists = False
        for tag in xdet_attributes.mega_tags:
            tag.exists = False
        
        if not self.objects_only:
            xdet_attributes.tags_string = ""
            xdet_attributes.user_tags.clear()
            xdet_attributes.mega_tags.clear()
            
            for p_tag in xdet_attributes.property_tags.split(","):
                new_tag = xdet_attributes.user_tags.add()
                new_tag.name = p_tag.strip()
                new_tag.state = "False"

        return {'FINISHED'}


classes = (
    UserTagsItem,
    MegaTagsItem,
    PrefabLinks,
    XDET_Attributes,
    UpdateUserTags,
    AddUserTag,
    RemoveUserTag,
    SelectSimilar,
    InvokeInputTagOperator,
    InvokeRenameTagOperator,
    ShowHideGroupOperator,
    PropertyTagIcon,
    PrefabLinksInfo,
    EngineTagsAddonPanel,
    RestoreDefault,
    SetDefaultParms,
    SelectLikeThis,
    ClearTags,
    ClearAllObjects,
    PreferencesPanel
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.xdet_attributes = bpy.props.PointerProperty(type=XDET_Attributes)

    bpy.app.handlers.load_post.append(pre_expand_tags)
    bpy.app.handlers.depsgraph_update_post.append(update_tags_by_select)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    if update_tags_by_select in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(update_tags_by_select)
    if pre_expand_tags in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(pre_expand_tags)
    
    del bpy.types.Scene.xdet_attributes


if __name__ == "__main__":
    register()