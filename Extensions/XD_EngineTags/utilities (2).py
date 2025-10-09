import bpy, re

def clean_list(input_list):
    """Очистка списка от проблемных элементов"""
    def _clean_spaces(input_list): # чистка от пробелов по концам
        return list(x.strip() for x in input_list)
    def _clean_emtys(input_list): # чистка от пустых элементов
        #for item in input_list:
            #if item == "":
                #input_list.remove(item)
        return list(filter(None, input_list))
    def _clean_doubles(input_list): # чистка от дубликатов
        return list(sorted(set(input_list)))

    input_list = _clean_spaces(input_list)
    input_list = _clean_emtys(input_list)
    input_list = _clean_doubles(input_list)
    return input_list

def clean_attrib_spaces(attrib):
    """Очистка атрибута от проблемных элементов"""
    def _clean_spaces(attrib): # чистка от пробелов по концам
        for item in attrib:
            item.name = item.name.strip()
    def _clean_emtys(attrib): # чистка от пустых элементов
        for i, item in enumerate(attrib):
            if item.name == "":
                attrib.remove(i)
    def _clean_doubles(attrib): # чистка от дубликатов
        item_list = list(sorted(set(item.name for item in attrib)))
        temp_dict = {}
        for name in item_list:
            attr_item = attrib.get(name)
            temp_dict[attr_item.name] = str(attr_item.state)
        attrib.clear()
        for name, state in temp_dict.items():
            new_item = attrib.add()
            new_item.name = name
            new_item.state = str(state)
            
    _clean_spaces(attrib)
    _clean_emtys(attrib)
    _clean_doubles(attrib)
    
    return attrib

def remove_empty_tags(object, pref_name="Tags"):
    tags = object.get(pref_name)
    if tags is not None:
        if tags == "":
            del object[pref_name]

def write_tags_to_object(object, pref_name="Tags") -> bool:
    """Запись тегов в атрибут объекта"""
    if bpy.context.scene.xdet_attributes.mega_mode:
        return
    
    if object.get(pref_name) is not None:
        del object[pref_name]
    object[pref_name] = bpy.context.scene.xdet_attributes.tags_string
    remove_empty_tags(object, pref_name)

def fix_non_latin(self,text):
    """Проверка на нелатинские символы"""
    matches = re.findall('[^a-zA-Z0-9.()_-]', text)
    if len(matches) > 0:
        for char in text:
            if char in matches:
                text = text.replace(char, "_")
        self.report({'WARNING'}, "New Tag has non-valid characters: " + str(matches))
    return text

def get_show_panel():
    """Определяем отображать ли элементы интерфейса."""
    active_object = bpy.context.view_layer.objects.active
    selected_objects = bpy.context.selected_objects
    bpy.context.scene.xdet_attributes.mega_mode = False
    
    if len(selected_objects) == 0 and active_object is not None:
        bpy.context.scene.xdet_attributes.show_panels = True
        bpy.context.scene.xdet_attributes.mega_mode = True
    elif len(selected_objects) == 1:
        bpy.context.scene.xdet_attributes.show_panels = True
    else:
        if check_similar(selected_objects):
            bpy.context.scene.xdet_attributes.show_panels = True
        else:
            bpy.context.scene.xdet_attributes.show_panels = True

def check_similar(objects) -> bool:
    """Проверка на то что объекты имеют одинаковые теги"""
    xdet_attributes = bpy.context.scene.xdet_attributes
    tags_items = set()
    
    for object in objects:
        if object.get("Tags") is not None:
            tags_items.add(object.get("Tags"))
        else:
            tags_items.add("")
            
    if len(tags_items) == 1:
        xdet_attributes.selected_is_similar = True
        return True
    else:
        xdet_attributes.selected_is_similar = False
        return False

def add_last_empty_tag():
    """Добавляем пустой тег в конец списка тегов user_tags."""
    user_tags = bpy.context.scene.xdet_attributes.user_tags
    
    if len(user_tags) > 0:
        if user_tags[-1].name != "":
            user_tags.add().name = ""
    else:
        user_tags.add().name = ""

def is_rename(current_user_tags, previous_user_tags, previous_act_object, previous_sel_objects):
    """
    Проверка того, что происходит в момент изменения текста в поле ввода.
    Если текущий объект равен предыдущему, то происходит переименование.
    В настоящее время функция не используется.
    """
    user_tags_list = [x.name for x in current_user_tags]
    user_tags_list = clean_list(user_tags_list)
    previous_user_tags = clean_list(previous_user_tags)
    
    selected_objects = bpy.context.selected_objects
    active_object = bpy.context.view_layer.objects.active
    
    if previous_act_object == active_object and previous_sel_objects == selected_objects and len(previous_user_tags) == len(user_tags_list) and previous_user_tags != user_tags_list:
        return True
    else:
        return False

def sort_tags(user_tags):
    """
    Сортировка тегов по алфавиту.
    
    На вход подается свойство с тегами, элементы которого будут отсортированы по алфавиту.
    """
    if len(user_tags) == 0: # если пусто
        return
        
    names_list = [tag.name for tag in user_tags]
    names_list = list(sorted(set(names_list)))
    states_list = [user_tags.get(name).state for name in names_list]
    
    user_tags.clear()
    for name, state in zip(names_list, states_list):
        new_tag = user_tags.add()
        new_tag.name = name
        new_tag.state = str(state)

def rewrite_mega_tags(user_tags):
    """
    Функция берет данные из user_tags и перезаписывает в mega_tags.
    
    :user_tags: свойство из xdet_attributes.
    """
    mega_tags = bpy.context.scene.xdet_attributes.mega_tags
    mega_states = {}
    
    for u_tag in user_tags:
        if u_tag.name in mega_tags:
            mega_states[u_tag.name] = str(mega_tags[u_tag.name].state)
        else:
            mega_states[u_tag.name] = "False"
            
    mega_tags.clear()
    for tag in user_tags:
        new_tag = mega_tags.add()
        new_tag.name = tag.name
        new_tag.state = str(mega_states[tag.name])
        new_tag.exists = tag.exists

def collect_objects_tags(objects):
    """Собираем теги всех объектов сцены."""
    objects_tags_list=[]
    
    if objects is None:
        return objects_tags_list
        
    if type(objects) is not bpy.types.bpy_prop_collection:
        if type(objects) is list:
            for object in objects:
                if object.get("Tags") is not  None:
                    obj_tags_list = object.get("Tags").split(",")
                    objects_tags_list += obj_tags_list
        else:
            print("type(objects):", type(objects))
    else:
        for object in objects:
            if object.get("Tags") is None:
                continue
            obj_tags_list = object.get("Tags").split(",")
            objects_tags_list += obj_tags_list
            
    objects_tags_list = clean_list(objects_tags_list) # чистим от пустых элементов
    objects_tags_list = list(sorted(set(objects_tags_list)))
    
    # просто на всякий случай убираем пробелы из всех тегов
    objects_tags_list_no_spaces = list(x.strip() for x in objects_tags_list)
    
    # дополнительно сортируем
    return list(sorted(set(objects_tags_list_no_spaces)))

def close_invoke_popup(x, y):
    """
    Функция для закрывания окна invoke_popup.
    
    При вызове курсор мыши уводится за пределы окна invoke_popup в результате чего окно закрывается.
    После этого курсор возвращается на прежнее место.
    
    :param x: Исходное положение курсора мыши по оси x.
    :param y: Исходное положение курсора мыши по оси y.
    """
    bpy.context.window.cursor_warp(10, 10)
    move_back = lambda: bpy.context.window.cursor_warp(x, y)
    bpy.app.timers.register(move_back, first_interval=0.001)

def get_prefab_links():
    """
    Функция находит на объектах атрибут PrefabLink.
    Это нужно для отображения предупреждения о наличии данного атрибута на объекете.
    """
    selected_objects = bpy.context.selected_objects
    bpy.context.scene.xdet_attributes.prefab_links.clear()
    
    for object in selected_objects:
        if object.get("PrefabLink") is not None:
            bpy.context.scene.xdet_attributes.prefab_links.add().name = object.name

def split_common_unical_tags(objects, user_tags):
    """
    Возвращает три списка тегов (list):
    - все теги выбранных объектов
    - уникальные теги - те, которые встречаются в одном объекте
    - общие теги - те, которые встречаются в нескольких объектах
    """
    # собираем теги со всех объектов в одну кучу
    all_tags_list = []
    common_tags_list = []
    unical_tags_list = []
    #partly_tags_list = [] # теги, встречающиеся в нескольких объектах
    for object in objects:
        if object.get("Tags") is None:
            for tag in user_tags:
                tag.state = "False"
            continue
            
        obj_tags_list = object.get("Tags").split(",")
        obj_tags_list = list(sorted(set(obj_tags_list))) # чистка и сортировка тегов
        obj_tags_list = clean_list(obj_tags_list) # чистим от пустых элементов
        all_tags_list += obj_tags_list
        
    # отделяем общие теги от уникальных
    for tag in all_tags_list:
        if all_tags_list.count(tag) < len(objects):
            unical_tags_list.append(tag)
        else:
            common_tags_list.append(tag)
            
        common_tags_list = list(set(common_tags_list))
        
    return all_tags_list, common_tags_list, unical_tags_list

def update_exist():
    """
    Обновление состояния стрелоке в зависимости от наличия атрибута в сцене.
    
    Происходит проверка всех объектов сцены на атрибут Tags.
    Если тег присутствует хотя бы раз, то стрелка включается, иначе выключается.
    """
    all_scene_objects = bpy.context.scene.objects
    all_scene_tags = []
    for object in all_scene_objects:
        if object.get("Tags") is not None:
            object_tags = object.get("Tags").split(",")
            object_tags = clean_list(object_tags)
            all_scene_tags += object_tags
    
    all_scene_tags = list(sorted(set(all_scene_tags)))

    for tag in bpy.context.scene.xdet_attributes.user_tags:
        if tag.name in all_scene_tags:
            tag.exists = True
        else:
            tag.exists = False

def debug_log(*args, enable=True):
    """
    Вывод дебага в консоль.
    """
    if not enable: return
    print(" ".join(args))