# TODO: протестировать аддон на blend сценах с Tank Force
# TODO: сцены лежат в папке Sources DONE
# TODO: если ничего не выделено, проверять и показывать наличие проблемных линков (с разной датой) DONE
# TODO: добавить кнопочку выделения всех объектов с текущим линком DONE
# TODO: если ничего не выбрано, то переходим в режим поиска DONE
# TODO: если у объекта включен блок (Library Override>Make>Selected), то блокировать поле ввода DONE
# TODO: если в режиме search mode введеный линк не существует, то кнопка поиска должна быть заблокирована DONE


import bpy
from .utilities import *
from .panels import *
from bpy.app.handlers import persistent


glob_prev_object = None # нужен для проверки "выбор другого объекта" или "ввод линка вручную"


class LinkedObjectItem(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(name="Object Name") # type: ignore


class TroubledObjectsItem(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(name="Object Name") # type: ignore


class XDPL_Attributes(bpy.types.PropertyGroup): # ПЕРЕДЕЛАТЬ СО СЦЕНЫ НА ОБЪЕКТ
    '''Основные атрибуты аддона'''
    def foo(self, context): # ПРИ ВЫДЕЛЕНИИ НЕСКОЛЬКИХ ОБЪЕКТОВ АТРИБУТ СТАНОВИТСЯ ОДИНАКОВЫМ ДЛЯ ВСЕХ.
        global glob_prev_object
        
        def _change_object_link(object): # переписываем PrefabLink у объекта
            self.enable_layout = True
            
            if self.prefab_link == "":
                if object.get("PrefabLink") is not None:
                    del object["PrefabLink"]
            else:
                object["PrefabLink"] = self.prefab_link
                
        active_object = get_active_object()
        selected_objects = bpy.context.selected_objects
        
        # если объект не изменился, это значит, что имя линка изменено вручную
        # если объект изменился, то это просто переключение объекта. Пропускаем.
        if glob_prev_object != active_object: return
        
        if len(selected_objects) < 2:
            _change_object_link(active_object)
        elif len(selected_objects) > 1:
            all_links = []
            for object in selected_objects:
                if object.get("PrefabLink") is not None:
                    all_links.append(object.get("PrefabLink"))
                else:
                    all_links.append("")
                    
            if len(set(all_links)) > 1:
                self.enable_layout = False
                return
            else:
                for object in selected_objects:
                    _change_object_link(object)
                    
            get_troubled_links()
        glob_prev_object = active_object
    
    prefab_link : bpy.props.StringProperty(name="Prefab Link", update=foo) # type: ignore
    search_link : bpy.props.StringProperty(name="Search Link") # type: ignore
    link_objects : bpy.props.CollectionProperty(type=LinkedObjectItem) # type: ignore
    is_troubled : bpy.props.StringProperty(name="Troubled Link", default="") # type: ignore
    troubled_objects : bpy.props.CollectionProperty(type=TroubledObjectsItem) # type: ignore
    enable_layout : bpy.props.BoolProperty(name="Enable Layout", default=True) # type: ignore
    enable_seach_button : bpy.props.BoolProperty(name="Enable Search Button", default=True) # type: ignore
    search_mode : bpy.props.BoolProperty(name="Search Mode", default=False) # type: ignore


def get_troubled_links():
    debug_log("Get Troubled Links")
    
    bpy.context.scene.xdpl_attributes.troubled_objects.clear()
    if is_no_objects(): return
    
    all_scene_objects = bpy.data.objects
    selected_objects = bpy.context.selected_objects
    
    def _get_different_object():
        if len(selected_objects) == 0: # если в режиме search mode
            # сначала делаем снапшот объектов сцены с линками, чтобы не гонять объекты в циклах
            all_scene_links = set()
            scene_snapshot = {}
            for object in all_scene_objects:
                link = object.get("PrefabLink")
                if link is not None:
                    scene_snapshot[object.name] = link
                    all_scene_links.add(link)
                    
            if len(all_scene_links) == 0: # прерываем когда нет линков в сцене
                return
                
            # если текущий линк не в all_scene_links то деактивируем кнопку поиска 
            if bpy.context.scene.xdpl_attributes.search_link not in all_scene_links:
                bpy.context.scene.xdpl_attributes.enable_seach_button = False
            else:
                bpy.context.scene.xdpl_attributes.enable_seach_button = True
                
            # группируем объекты по присвоенным линкам
            links_dict = {}
            for link in all_scene_links:
                obj_group = set()
                for object_name, object_link in scene_snapshot.items():
                    if object_link == link:
                        obj_group.add(object_name)
                links_dict[link] = obj_group # получаем формат {link: {объекты с этим линком}}
                
            # проверяем data сгруппированных объектов
            for link, obj_group in links_dict.items():
                if len(obj_group) < 2:
                    continue
                    
                datas = set()
                for object_name in obj_group:
                    object = bpy.data.objects[object_name]
                    if object.data is None:
                        continue
                    else:
                        datas.add(object.data)
                        
                if len(datas) > 1:
                    bpy.context.scene.xdpl_attributes.is_troubled = "Some PrefabLink objects have different data!"
                    for object_name in obj_group:
                        bpy.context.scene.xdpl_attributes.troubled_objects.add().name = object_name
                        
        elif len(selected_objects) > 0: # если есть выделенные объекты
            active_object = get_active_object()
            active_object_link = active_object.get("PrefabLink")
            
            if active_object_link is None:
                return
                
            # получаем все линки в сцене
            all_links = set()
            for object in all_scene_objects:
                if object.get("PrefabLink") is not None:
                    all_links.add(object.get("PrefabLink"))
                    
            # определяем проблемные объекты относительно линка активного объекта
            all_data = set()
            for object in all_scene_objects:
                if object.get("PrefabLink") == active_object_link:
                    all_data.add(object.data)
            if len(all_data) > 1:
                bpy.context.scene.xdpl_attributes.is_troubled = "Assigned to Different Data Objects!"
                
            # если линк проблемный - получаем объекты с этим линком
            if bpy.context.scene.xdpl_attributes.is_troubled:
                for object in all_scene_objects:
                    if object.get("PrefabLink") == active_object_link:
                        bpy.context.scene.xdpl_attributes.troubled_objects.add().name =  object.name
            else:
                bpy.context.scene.xdpl_attributes.troubled_objects.clear()
                
    def _get_linked_objects(objects):
        # ЕСЛИ СРЕДИ ОБЪЕКТОВ ЕСТЬ ЛИНКИ
        is_obj_links = []
        for obj in objects:
            if obj.library is not None:
                bpy.context.scene.xdpl_attributes.enable_layout = False
                is_obj_links.append(obj)
                bpy.context.scene.xdpl_attributes.troubled_objects.add().name = obj.name
                
        if len(is_obj_links) == 0:
            return
        #bpy.context.scene.xdpl_attributes.is_troubled = f"{len(is_obj_links)} of the selected objects is a Link!" # отображение предупреждения о объекте-линке
        
    _get_different_object() # если текущий линк назначен на объекты с разной датой
    _get_linked_objects(selected_objects) # если объекты являются линками


def update_xdpl_attributes():
    def _read_prefab_link_from_objects(a_object): # читаем PrefabLink с объектов и записываем его в класс
        def _read_single_object(work_object): # читаем PrefabLink с одного объекта
            global glob_prev_object
            
            work_object_link = work_object.get("PrefabLink")
            if work_object_link is not None:
                if work_object != glob_prev_object: # если объект изменился значит это не изменение линка а переключение объекта
                    new_item = bpy.context.scene.xdpl_attributes
                    new_item.prefab_link = work_object_link
                    new_obj = new_item.link_objects.add()
                    new_obj.name = work_object.name
            else:
                if work_object != glob_prev_object: # если объект изменился значит это не изменение линка а переключение объекта
                    new_item = bpy.context.scene.xdpl_attributes
                    new_item.prefab_link = ""
                    new_obj = new_item.link_objects.add()
                    new_obj.name = work_object.name
                    
            glob_prev_object = work_object
            
        # 
        s_objects = bpy.context.selected_objects
        if len(s_objects) < 2:
            _read_single_object(a_object)
        elif len(s_objects) > 1:
            all_links = []
            for object in s_objects:
                if object.get("PrefabLink") is not None:
                    all_links.append(object.get("PrefabLink"))
                else:
                    all_links.append("")
            if len(set(all_links)) > 1:
                bpy.context.scene.xdpl_attributes.enable_layout = False
                pass
                
            for object in s_objects:
                _read_single_object(object)
                
    if is_no_objects(): return
    _read_prefab_link_from_objects(get_active_object())


@persistent
def init_scene(dummy):
    '''Инициализация аддона в сцене'''
    debug_log("Init Scene")
    bpy.context.scene.xdpl_attributes.enable_layout = True
    bpy.context.scene.xdpl_attributes.is_troubled = ""
    init_search_mode()
    update_xdpl_attributes()
    get_troubled_links()


@persistent
def manual_re_init(scene):
    '''Обновление состояния аддона при выборе другого объекта'''
    debug_log("Manual Re Init")
    bpy.context.scene.xdpl_attributes.enable_layout = True
    bpy.context.scene.xdpl_attributes.is_troubled = ""
    init_search_mode()
    update_xdpl_attributes()
    get_troubled_links()


class AddPrefabLink(bpy.types.Operator):
    #Добавляем новый Prefab Link
    bl_idname = "scene.add_prefab_link"
    bl_label = "Add Prefab Link"
    bl_description = "Add Prefab Link"
    #bl_options = {'REGISTER', 'INTERNAL'}
    
    tag_name : bpy.props.StringProperty() # type: ignore
    
    def execute(self, context):
        xdpl_attributes = bpy.context.scene.xdpl_attributes
        debug_log(self.bl_label)
        return {'FINISHED'}


class SelectLinkedObjects(bpy.types.Operator):
    '''Выбираем объекты по линку'''
    bl_idname = "scene.select_linked_objects"
    bl_label = "Select Linked Objects"
    bl_description = "Select Linked Objects"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        debug_log(self.bl_label)
        
        if bpy.context.scene.xdpl_attributes.search_mode:
            link = bpy.context.scene.xdpl_attributes.search_link
        else:
            link = bpy.context.scene.xdpl_attributes.prefab_link
            
        all_scene_objects = bpy.data.objects
        
        # получаем объекты с этим линком
        to_select_objs = []
        for object in all_scene_objects:
            prefab_link = object.get("PrefabLink")
            if prefab_link is None:
                continue
            if prefab_link == link:
                to_select_objs.append(object)
                
        # снимаем выделение со всех объектов
        for object in all_scene_objects:
            object.select_set(False)
            
        # выделяем объекты
        for object in to_select_objs:
            object.select_set(True)
            
        # устанавливаем активный объект
        if len(to_select_objs) > 0:
            bpy.context.view_layer.objects.active = to_select_objs[0]
            
        return {'FINISHED'}


classes = (
    LinkedObjectItem,
    TroubledObjectsItem,
    XDPL_Attributes,
    AddPrefabLink,
    SelectLinkedObjects,
    TroubledLinksOperator,
    EnginePrefabLinkAddonPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.xdpl_attributes = bpy.props.PointerProperty(type=XDPL_Attributes)
    
    bpy.app.handlers.load_post.append(init_scene)
    bpy.app.handlers.depsgraph_update_post.append(manual_re_init)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    if manual_re_init in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(manual_re_init)
        
    if init_scene in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(init_scene)
        
    del bpy.types.Scene.xdpl_attributes


if __name__ == "__main__":
    register()