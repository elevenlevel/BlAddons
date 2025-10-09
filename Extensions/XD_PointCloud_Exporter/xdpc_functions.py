import bpy

PROXY_COLLECTION_NAME = "XD_PROXY_COLLECTION"
EMITTER_PREFIX = "XD_SCATTER_"
EMITTER_MODIFIER = "XD_PointCloud_GENERATOR"

EMITTER_OBJECT_SOCKET = "Socket_2"
INSTANCES_COLLECTION_SOCKET = "Socket_13"
CONVERT_TO_POINTS_SOCKET = "Socket_4"
DISTANCE_MIN_SOCKET = "Socket_5"
DISTANCE_MAX_SOCKET = "Socket_6"
SEED_SOCKET = "Socket_7"
NORMAL_FACTOR_SOCKET = "Socket_9"
SCALE_FACTOR_SOCKET = "Socket_10"
COLOR0_ATTRIBUTE_SOCKET = "Socket_11"
UV0_ATTRIBUTE_SOCKET = "Socket_12"

def set_index_attribute():
	print("Hello World!")

def add_empty_emitter():
    """Добавляет пустой элемент в список емиттеров для отображение строки +"""
    emit_list = bpy.context.scene.xdpc_attributes.emit_list
    emit_count = len(emit_list)
    
    if emit_count == 0:
        new_item = emit_list.add()
        new_item.index = 0
        new_item.name = ""
        new_item.type = "ADD"
	
def unname_emitter_item(emitter_index):
    """Сбрасываем имя текущего эмиттера"""
    emit_list = bpy.context.scene.xdpc_attributes.emit_list
    emit_list[emitter_index].name = "" # сбрасываем название эмиттера

def remove_emitter_item(emitter_index):
    """Удаление эмиттера из emit_list по индексу"""
    bpy.context.scene.xdpc_attributes.emit_list.remove(emitter_index)
    print("Emitter " + str(emitter_index) + " удален!")

def remove_emitter_object(emitter_name):
    """Удаляем объект только если рабочая коллекция существует"""
    if bpy.data.collections.get(PROXY_COLLECTION_NAME):
        scatter_collection = bpy.data.collections.get(PROXY_COLLECTION_NAME)
        objects = scatter_collection.all_objects
        full_emitter_name = EMITTER_PREFIX + emitter_name
        
        if full_emitter_name in objects:
            bpy.data.objects.remove(bpy.data.objects[full_emitter_name], do_unlink=True)

def update_instances_when_object_changed():
    """Обновление инстансов при изменениях в коллекции инстансов"""

    emit_list = bpy.context.scene.xdpc_attributes.emit_list
    
    for emitter in emit_list:
        if emitter.inst_list:
            instance_collection = emitter.emitter_collection
            instance_objects = instance_collection.objects

            for idx, instance in enumerate(emitter.inst_list):
                if instance.name not in instance_objects:
                    emitter.inst_list.remove(idx)
            for object in instance_objects:
                if object.name not in emitter.inst_list:
                    new_instance = emitter.inst_list.add()
                    new_instance.name = object.name
                    new_instance.type = "INSTANCE"
                    new_instance.enabled = True
                    new_instance.factor = 0
                    new_instance.instance = object
                    # emitter.inst_list.append(new_instance)

def remove_emitter_when_object_deleted():
    """Удаление эмиттера при удалении объекта из прокси-коллекции"""
    if PROXY_COLLECTION_NAME not in bpy.data.collections: # если коллекция существует в сцене
        return
    
    proxy_collection = bpy.data.collections.get(PROXY_COLLECTION_NAME)
    proxy_objects = proxy_collection.objects
    emit_list = bpy.context.scene.xdpc_attributes.emit_list

    for emitter in emit_list:
        if EMITTER_PREFIX + emitter.name not in proxy_objects:
            if emitter.type == "EMITTER" and emitter.name != "":
                print(emitter.name + " удален!")
                bpy.context.scene.xdpc_attributes.emit_list.remove(emitter.index)


def recalc_instances_factors():
    """Пересчёт факторов инстансов эмиттера"""
    emit_list = bpy.context.scene.xdpc_attributes.emit_list

    for emitter in emit_list:
        factor_list = []
        
        for instance in emitter.inst_list:
            if instance.type == "ADD": continue
            factor_list.append(instance.factor)
        
        factor_summ = sum(factor_list)
        
        if factor_summ > 1.0:
            for instance in emitter.inst_list:
                if instance.type == "ADD": continue
                instance.factor_result = float(instance.factor / factor_summ)

def remove_empty_proxy_collection():
    """Удаление пустой прокси коллекции"""
    if PROXY_COLLECTION_NAME in bpy.data.collections: # если коллекция существует в сцене
        proxy_collection = bpy.data.collections.get(PROXY_COLLECTION_NAME)
        if not proxy_collection.all_objects: # если коллекция пустая
            bpy.data.collections.remove(proxy_collection)

def remove_proxy_objects(emitter_index):
    """Удаление прокси-объектов из прокси-коллекции"""
    
    # если прокси коллекции не существует, то останавливаем выполнение
    if PROXY_COLLECTION_NAME not in bpy.data.collections: return
    proxy_collection = bpy.data.collections.get(PROXY_COLLECTION_NAME)
    
    # если прокси коллекция пуста, то останавливаем выполнение
    if not proxy_collection.objects: return
    proxy_objects = proxy_collection.objects
    
    emit_list = bpy.context.scene.xdpc_attributes.emit_list
    proxy_name = EMITTER_PREFIX + emit_list[emitter_index].name
    
    # если в прокси коллекции нет объекта текущего эмиттера, то останавливаем выполнение
    if proxy_name not in proxy_objects: return
    
    if proxy_name in bpy.data.objects:
        proxy_object = bpy.context.scene.objects.get(proxy_name)
        bpy.data.objects.remove(proxy_object)

def clean_instances_of_empty_emitter():
    """Удаление инстансов эмиттера, когда эмиттер удаляется из списка"""
    emit_list = bpy.context.scene.xdpc_attributes.emit_list
    
    for emitter in emit_list:
        if emitter.type == "EMITTER" and emitter.name == "":
            emitter.inst_list.clear()
            
            for idx, inst in enumerate(emit_list): # пересчитываем индексы для правильной нумерации
                inst.index = idx
                emit_list[0].enabled = True

def sort_emitters_indices():
    emit_list = bpy.context.scene.xdpc_attributes.emit_list

    for idx, emitter in enumerate(emit_list):
        if emitter.type == "EMITTER":
            emitter.index = idx

def reset_active_index():
    emit_list = bpy.context.scene.xdpc_attributes.emit_list
    active_index = bpy.context.scene.xdpc_attributes.emit_idx
    
    if active_index > len(emit_list) - 2:
        bpy.context.scene.xdpc_attributes.emit_idx = len(emit_list) - 1
'''
def set_emitters_postfix(self):
    """Назначаем postfix каждому новому эмиттеру"""
    emit_list = bpy.context.scene.xdpc_attributes.emit_list

    # сначала собираем все имена эмиттеров в список
    names = []
    postfixes = []

    for emitter in emit_list:
        if emitter.type == "ADD":
            continue
        if emitter.name:
            names.append(emitter.name)
            postfixes.append(emitter.postfix)
    
    # далее считаем количество повторяющихся имен в списке
    count_dict = count_list_elements(names)

    i = 0
    for emitter in emit_list:
        if emitter.type == "ADD":
            continue
        
        emitter_count = count_dict[emitter.name]
        if emitter_count > 1 and emitter.name:
            i += 1
            if emitter.postfix == -1:


    
    print("Postfix: " + str(self.postfix))

    return postfix
'''
def count_list_elements(my_list):
    """Подсчёт количества повторяющихся элементов в списке"""
    counts = {}
    for element in my_list:
        if element in counts:
            counts[element] += 1
        else:
            counts[element] = 1
    return counts

def set_modifier_fields(self):
    """Установка полей модификатора"""
    emitter = self.emitter

    # всякие проверки
    if PROXY_COLLECTION_NAME not in bpy.data.collections: return
    
    proxy_collection = bpy.data.collections.get(PROXY_COLLECTION_NAME)
    emitter_proxy_name = EMITTER_PREFIX + emitter.name

    if emitter_proxy_name not in proxy_collection.objects: return

    emitter_proxy = proxy_collection.objects.get(emitter_proxy_name)

    if EMITTER_MODIFIER not in emitter_proxy.modifiers: return

    # получаем ссылку на модификатор
    modifier = emitter_proxy.modifiers.get(EMITTER_MODIFIER)

    # установка значений полей
    modifier[EMITTER_OBJECT_SOCKET] = emitter
    modifier[INSTANCES_COLLECTION_SOCKET] = self.emitter_collection
    modifier[CONVERT_TO_POINTS_SOCKET] = False
    modifier[DISTANCE_MIN_SOCKET] = 0.0
    modifier[DISTANCE_MAX_SOCKET] = 0.2
    modifier[SEED_SOCKET] = 0
    modifier[NORMAL_FACTOR_SOCKET] = 1.0
    modifier[SCALE_FACTOR_SOCKET] = 1.0
    modifier[COLOR0_ATTRIBUTE_SOCKET] = "Color"
    modifier[UV0_ATTRIBUTE_SOCKET] = "UVSet0"