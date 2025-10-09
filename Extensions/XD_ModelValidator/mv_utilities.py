import bpy
import time, json, math, mathutils, bmesh
import datetime

def spent_timer(func):
    '''декоратор для подсчета затраченного времени'''
    def wrapper(context, check_type):
        start_time = time.time()

        func(context, check_type)
        result_time = time.time() - start_time
    
        formatted_time = convert_float_time(result_time)

        bpy.context.scene.mv_attributes.checkboxes[check_type].time = formatted_time
        bpy.context.scene.mv_attributes.spent_time += result_time
    return wrapper

def save_scene():
    '''Сохранение сцены'''
    if bpy.data.filepath:
        bpy.ops.wm.save_mainfile()
    else:
        bpy.ops.wm.save_as_mainfile('INVOKE_DEFAULT')

def if_scene_dirty(func):
    '''Если сцена не сохранена'''
    def wrapper(self, context):
        if bpy.data.is_dirty:
            bpy.types.Scene.proceed_function = func
            return bpy.ops.object.save_dialog('INVOKE_DEFAULT')
        else:
            return func(self, context)
    return wrapper

def rest_editor_state(func):
    '''Декоратор для возвращения редактора в исходное состояние после проверки'''
    def wrapper(context, check_type):
        # сохраняем текущий режим редактора
        old_mode = bpy.context.mode if bpy.context.mode != 'EDIT_MESH' else 'EDIT'

        # переходим в режим объекта
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # запоминаем активный объект
        if bpy.context.view_layer.objects.active is not None:
            old_active = bpy.context.view_layer.objects.active
        else:
            old_active = None
        
        # запоминаем выделенные объекты
        old_selected = bpy.context.selected_objects 
        
        # сбрасываем выделенный и активный объекты
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = None

        func(context, check_type) # ВЫПОЛНЯЕМ ПРОВЕРКУ

        # возвращаем активный до проверки объект
        if old_active is not None:
            bpy.context.view_layer.objects.active = old_active
        else:
            bpy.context.view_layer.objects.active = bpy.context.view_layer.objects[0]
        
        # возвращаем выделение объектов
        for object in old_selected:
            object.select_set(True)

        # возвращаем режим редактора
        bpy.ops.object.mode_set(mode=old_mode)
    return wrapper

def update_checkboxes_count():
    # собираем данные о количестве включенных чекбоксов в каждой группе и в общей сумме
    groups = []
    all_active_checks_count = 0
    bpy.context.scene.mv_attributes.checkboxes_count.clear()

    for item in bpy.context.scene.mv_attributes.checkboxes:
        if item.state:
            all_active_checks_count += 1

        # пропуск, если группа уже добавлена
        if item.group in groups:
            continue
        groups.append(item.group)

        new = bpy.context.scene.mv_attributes.checkboxes_count.add()
        
        group_name = item.group
        group_length = 0
        active_checks_count = 0

        for checkbox in bpy.context.scene.mv_attributes.checkboxes:
            if checkbox.group == group_name:
                group_length += 1
            if checkbox.state and checkbox.group == group_name:
                active_checks_count += 1
        
        new.group_name = group_name
        new.active_count = active_checks_count
        new.group_length = group_length
    
    for item in bpy.context.scene.mv_attributes.checkboxes_count:
        item.all_active_count = all_active_checks_count

def main_sort_by_color(context):
    # бэкапим hide_state в issues чтобы сохранить состояние во время сортировки
    for report in context.scene.formate_report:
        issue = context.scene.issues[report.name].hide_state = report.hide_state

    # перестраиваем report в соответствии с цветами
    context.scene.formate_report.clear()

    def _combine_reports():
        report_line = context.scene.formate_report.add()
        report_line.name = issue.name
        report_line.header = issue.header
        report_line.text = issue.text
        report_line.success = issue.success
        report_line.hide_state = issue.hide_state

    if context.scene.mv_attributes.sort_by_color:
        for issue in context.scene.issues:
            if issue.success in ["[WARNING]", "[FAILED]"]:
                _combine_reports()
        
        if not context.scene.mv_attributes.hide_green:
            for issue in context.scene.issues:
                if issue.success == "[SUCCESS]":
                    _combine_reports()
    else:
        if context.scene.mv_attributes.hide_green:
            for issue in context.scene.issues:
                if issue.success == "[SUCCESS]":
                    continue
                _combine_reports()
        else:
            for issue in context.scene.issues:
                _combine_reports()
            

def formate_result_string(context, check_type, success, checked_objects):
    # метод формирования результатов единичной проверки в список строк
    header, text, icons = [], [], []

    # типы объектов
    type_icons = {"EMPTY":"EMPTY_DATA", "MESH":"MESH_DATA", "CURVE":"CURVE_DATA", "FONT":"FONT_DATA", "META":"META_DATA", "ARMATURE":"ARMATURE_DATA", "LATTICE":"LATTICE_DATA", "CAMERA":"CAMERA_DATA", "LIGHT":"LIGHT_DATA"}
    
    # формируем заголовок
    header = f'{check_type}: {success}'
    
    # формируем текст
    if success in ["[FAILED]", "[WARNING]"]:
        for object in checked_objects:
            mesh_type = checked_objects[object][0]

            # назначение иконки
            if mesh_type == "COLL":
                type_icon = "OUTLINER_COLLECTION"
            elif mesh_type == "EMPTY":
                type_icon = "EMPTY_DATA"
            elif mesh_type == "OBJECT":
                type_icon = "ERROR" if "!!!" in object else type_icons[bpy.context.scene.objects[object].type]
            else:
                type_icon = "MESH_DATA"
            
            icons.append(type_icon)

            if mesh_type in ["FACE", "EDGE", "VERT"]: # если объект типа меш
                el_types_dict = {"FACE":"faces", "EDGE":"edges", "VERT":"vertices"}
                element_type =  el_types_dict[mesh_type]

                element_list = checked_objects[object][1]
                element_count = len(element_list)
                
                issue_string = "└ {}: {} {}".format(object, element_count, element_type)
                text.append({"issue_string":str(issue_string), "object":str(object), "mesh_type":str(mesh_type), "type_icon":str(type_icon), "element_list":str(element_list)})
            
            else: # если объект типа коллекция или empty
                el_types_dict = {"COLL":"collections", "EMPTY":"emptys", "OBJECT":"objects"}
                element_type =  el_types_dict[mesh_type]

                issue_string = object
                text.append({"issue_string":str(issue_string), "object":str(object), "mesh_type":str(mesh_type), "type_icon":str(type_icon)})

    #if bpy.context.scene.issues item already exists
    if check_type in bpy.context.scene.issues:
        issue = bpy.context.scene.issues[check_type]
    else:
        issue = bpy.context.scene.issues.add()
    issue.name = check_type
    issue.header = str(header)
    issue.text = json.dumps(text)
    issue.success = success

    main_sort_by_color(context)

    # устанавливаем цвет иконки в зависимости от результата
    colors_dict = {"[SUCCESS]":"GREEN", "[WARNING]":"YELLOW", "[FAILED]":"RED", "":"GRAY"}
    success_color = colors_dict[success]
    #success_color = 'RED' if success == "[FAILED]" else 'YELLOW' if success == "[WARNING]" else 'GREEN' if success == "[SUCCESS]" else 'GRAY' 
    bpy.context.scene.mv_attributes.checkboxes[check_type].color = success_color

def set_warning_type(check_type):
    # устанавливаем цвет ошибки в зависимости от указанного в интерфейсе (W/E)
    warning_type = bpy.context.scene.mv_attributes.checkboxes[check_type].warning_type

    if warning_type:
        success = "[WARNING]"
    else:
        success = "[FAILED]"
    
    return success

def select_check_entities(entities_type="all"): # all, objects, collections
    # выбираем нужные объекты в зависимости от положения чекбокса check_active
    if bpy.context.scene.mv_attributes.check_active:
        # по активной коллекции
        return get_active_collection()[entities_type]
    else:
        # по всей сцене
        return get_all_of_scene()[entities_type]

def __face_neighbours(object, face) -> set:
    # метод определения соседей полигона. Возвращаем номера полигонов
    neighbours = set()

    for subface in object.data.polygons:
        # пропускаем совпадение полигона
        if subface.index == face.index: continue
        
        # определяем общие ребра
        common_edges = set(face.edge_keys) & set(subface.edge_keys)

        if common_edges != set():
            neighbours.add(subface.index)

    return neighbours

def convert_float_time(float_time):
    seconds = float_time % (24 * 3600)
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds %= 60
    seconds = round(seconds, 2)

    result =  "{}{}{}s".format(
        "" if hours == 0 else "{}h".format(hours),
        "" if minutes == 0 else "{}m".format(minutes),
        seconds)

    return result

def get_active_collection() -> dict:
    # получаем активную коллекию
    active_collection = bpy.context.collection
    # все коллекции активной коллекции кроме самой активной коллекции
    collections = active_collection.children_recursive
    # все объекты активной коллекции
    all_objects = active_collection.all_objects

    # список всех коллекций активной коллекции
    all_collections = [active_collection]
    # список всех элементов активной коллекции
    all_entities = [active_collection]

    for collection in collections:
        all_collections.append(collection)
        all_entities.append(collection)
    for object in all_objects:
        all_entities.append(object)
    
    return {"collections": all_collections, "objects": all_objects, "all": all_entities}

def get_all_of_scene() -> dict:
    # коллекция сцены
    scene_collection = bpy.context.scene.collection
    # все коллекции в сцене кроме коллекции сцены
    collections = scene_collection.children_recursive
    # все объекты в сцене
    all_objects = bpy.context.scene.objects

    # список всех коллекций в сцене
    all_collections = [scene_collection]
    # список всех объектов в сцене
    all_entities = [scene_collection]

    for collection in collections:
        all_collections.append(collection)
        all_entities.append(collection)
    for object in all_objects:
        all_entities.append(object)
    
    return {"collections": all_collections, "objects": all_objects, "all": all_entities}

def reset_color_labels(context, check_type):
    context.scene.mv_attributes.checkboxes[check_type].color = "GRAY"

def calc_progress_factor(context, progress_factor=0):
    active_checks = bpy.context.scene.mv_attributes.checkboxes_count[0].all_active_count
    progress_factor += 1

    #progress_factor = progress_factor / active_checks
    bpy.context.scene.mv_attributes.progress_factor = progress_factor

    return progress_factor

def set_active_collection(layers, collection):
	for layer in layers.children:
		if layer.name == collection.name:
			bpy.context.view_layer.active_layer_collection = layer
			break
		else:
			set_active_collection(layer, collection)

def redraw_progress_bar(iter):
	# обновление прогресса для прогресс бара
	#active_count = bpy.context.scene.mv_attributes.checkboxes_count[0].all_active_count
    progress_factor = iter / len(bpy.context.scene.mv_attributes.checkboxes)
    bpy.context.scene.mv_attributes.progress_factor = progress_factor
    # обновление интерфейса
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)