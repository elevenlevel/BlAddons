import bpy
import json
from mathutils import Vector
import os

def get_matlayers_path(ml_path):
    """
    Формирует путь до MatLayers~ файла даже если выбран файл без тильды

    :param ml_path: путь до текущего MatLayers файла
    """

    if ml_path == "":
        return None
    
    if not ml_path.endswith("~"):
        ml_path = ml_path + "~"
    
    return ml_path

def get_file_name(ml_path):
    """
    Возвращает имя MatLayers файла

    :param ml_path: путь до текущего MatLayers файла
    """

    mat_layers_file = get_matlayers_path(ml_path)
    return os.path.splitext(os.path.basename(mat_layers_file))[0]

def get_matlayers_data(ml_path):
    """
    Читает дату из MatLayers файла

    :param ml_path: путь до текущего MatLayers файла
    """

    mat_layers_file = get_matlayers_path(ml_path)
    
    # читаем содержиме файла *.MatLayers
    try:
        with open(mat_layers_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except:
        return None

def get_active_material():
    """
    Возвращает текущий активный материал
    """

    context = bpy.context
    space = context.space_data
    
    # Проверяем, что мы в редакторе узлов и это Shader Editor
    if space.type == 'NODE_EDITOR' and space.tree_type == 'ShaderNodeTree':
        # Получаем активный материал
        if space.node_tree is not None:
            # Для объектов
            if space.shader_type == 'OBJECT':
                obj = context.active_object
                if obj and obj.active_material:
                    return obj.active_material
            # Для мировых шейдеров
            elif space.shader_type == 'WORLD':
                return context.scene.world
    return None

def get_active_tree():
    """
    Возвращает текущее активное дерево нод
    """

    active_material = get_active_material()
    space = get_node_editor()

    if active_material is not None:
        tree = space.edit_tree
        if tree.type != "SHADER":
            return None
        
        if tree.name == "Shader Nodetree":
            target_tree = active_material.node_tree
        else:
            target_tree = tree
        
        return target_tree

def get_active_node(target_tree):
    """
    Возвращает активную ноду
    
    :param target_tree: целевое дерево нод
    """

    selected_nodes = [node for node in target_tree.nodes if node.select]

    if len(selected_nodes) != 0:
        result = target_tree.nodes.active
    else:
        result = None
    return result

def get_node_editor():
    """
    Возвращает окно node_editor
    """

    space = bpy.context.space_data

    # Проверяем, что мы в Node Editor
    if space.type != 'NODE_EDITOR':
        return None
    return space

def get_node_editor_center():
    """
    Возвращает центр видимой области Node Editor в координатах пространства нод.
    
    Returns:
        Vector(x, y) — центр в координатах нод, или по нулям если Node Editor не найден
    """

    for area in bpy.context.screen.areas:
        if area.type == 'NODE_EDITOR':
            # Находим основную область (где отображаются ноды)
            region = next((r for r in area.regions if r.type == 'WINDOW'), None)
            if not region:
                continue
            
            # Получаем объект View2D
            view2d = region.view2d
            
            # Углы региона в пикселях (левый нижний и правый верхний)
            x1, y1 = 0, 0  # левый нижний угол региона
            x2, y2 = region.width, region.height  # правый верхний угол
            
            # Преобразуем пиксели в координаты нод
            cx1, cy1 = view2d.region_to_view(x1, y1)  # левый нижний
            cx2, cy2 = view2d.region_to_view(x2, y2)  # правый верхний
            
            # Центр — среднее между углами
            center_x = (cx1 + cx2) / 2
            center_y = (cy1 + cy2) / 2
            
            return Vector((center_x, center_y))
    return Vector((0.0, 0.0))

def find_new_node_location(node_tree, start_pos=Vector((0, 0)), grid_size=50):
    """
    Ищет свободное место на сетке пространства node_editor

    :param node_tree: дерево нод
    :param start_pos: позиция, от которой начинаем отсчет
    :param grid_size: размер ячейки для итераций проверки
    """

    x, y = start_pos.x, start_pos.y
    
    while True:
        # Проверяем текущую позицию
        occupied = any(
            abs(node.location.x - x) < grid_size and 
            abs(node.location.y - y) < grid_size
            for node in node_tree.nodes
        )
        
        if not occupied:
            return Vector((x, y))
        
        # Сдвигаем по диагонали
        x += grid_size
        y -= grid_size


def remove_group_node(active_tree,
                    active_node):
    """
    Удаляет активную ноду
    
    :param active_tree: активное дерево нод
    :param active_node: активная нода
    """

    node_tree = active_node.node_tree
    active_tree.nodes.remove(active_node)

    if node_tree:
        bpy.data.node_groups.remove(node_tree)


def add_single_node(tree,
                    node_type: str='ShaderNodeTexImage',
                    loc_x: float=0.0,
                    loc_y: float=0.0):
    """
    Создает одну любую ноду

    :param node_type: тип создаваемой ноды
    :param loc_x: расположение создаваемой ноды по X
    :param loc_y: расположение создаваемой ноды по Y
    """

    new_node = tree.nodes.new(node_type)
    new_node.location = (loc_x, loc_y)

    return new_node

def set_socket_value(node,
                    socket_name: str,
                    value):
    """
    Задает значение для сокета ноды
    
    :param node: нода с кторой работаем
    :param socket_name: имя сокета
    :param value: значение
    """
        
    for input_socket in node.inputs:
        if input_socket.name == socket_name:
            input_socket.default_value = value  # Красный
            break

def get_img_file(layer):
    """
    Читает файл изображения с диска
    
    :param layer: слой (или путь до изображения) ???
    """

    if os.path.exists(layer):
        img = bpy.data.images.load(layer, check_existing=True)
        return img, None
    else:
        return None, "NO_TEXTURE"  # Флаг ошибки

def check_existing_textures(ml_path):
    """
    Проверка на существование указанные в MatLayers файле текстуры
    
    :param ml_path: путь до текущего MatLayers файла
    """

    matlayers_data = get_matlayers_data(ml_path)
    matlayers_layers = matlayers_data['layers']
    file_path = get_matlayers_path(ml_path)

    bad_textures = bpy.context.scene.bad_textures
    for layer in matlayers_layers:
        for key, value in layer.items():
            if key == "albedo" or key == "geometry":
                abs_path = os.path.abspath(os.path.join(file_path, value))
                if not os.path.exists(abs_path):
                    new_bad_texture = bad_textures.add()
                    new_bad_texture.texture = abs_path
    
    if len(bpy.context.scene.bad_textures) > 0:
        bpy.ops.scene.show_no_texture_dialog('INVOKE_DEFAULT')
        return False
    else:
        return True

def remove_ghosted_groups():
    """
    Ищет и удаляет лишние группы-призраки (при удалении групповой ноды, она остается в файле и занимает имя)
    """
        
    ghosts = []
    for group in bpy.data.node_groups:
        # Пропускаем если есть пользователи
        if group.users != 0:
            continue

        # Пропускаем если fake user
        if group.use_fake_user:
            continue
        
        active_material = get_active_material()
        # если активный материал вообще есть
        if not active_material:
            continue
        
        # Проверяем реальное использование
        is_really_used = False

        if active_material.use_nodes and active_material.node_tree:
            for node in active_material.node_tree.nodes:
                if node.type == 'GROUP' and node.node_tree == group:
                    is_really_used = True
                    break
        
        if not is_really_used:
            ghosts.append(group)
    
    for g in ghosts:
        try:
            bpy.data.node_groups.remove(g)
        except:
            print(f"Не удалось удалить: {g.name}")

def construct_group_node(active_tree: bpy.types.ShaderNodeTree,
                        matlayers_data: dict,
                        group_parms: str,
                        ml_path: str) -> None:
        """
        Основная функция сборщик групповой MatLayers ноды
        
        :param active_tree: текущее дерево нод
        :param matlayers_data: данные из MatLayers Файла
        :param group_parms: параметры ноды (цвет, локация и т.д.)
        :param ml_path: путь до текущего MatLayers файла
        """
        
        if not active_tree:
            print("Ошибка: active_tree не указан")
            return None
    
    ###===БЛОК ПОДГОТОВКИ ДАННЫХ===
        file_name = get_file_name(ml_path) # имя файла *.MatLayers

        if group_parms == None: # Если нода новая
            group_name = f"{file_name} MAT LAYERS"
        else: # Если это апдейт ноды
            group_name = group_parms['name']
        
        current_path = get_matlayers_path(ml_path)
        matlayers_layers = matlayers_data['layers']


    ###===БЛОК СОЗДАНИЯ ОСНОВНОЙ ГРУППЫ===###
        # Создаём новое дерево нод (NodeTree) для основной группы
        main_group_tree = bpy.data.node_groups.new(type='ShaderNodeTree', name=group_name)
        
        # Добавляем ноду‑группу в целевой NodeTree
        main_group_node = add_single_node(active_tree, 'ShaderNodeGroup', 0, 0)
        
        layers = main_group_node.shader_links.layers
        
        for layer in matlayers_layers:
            albedo_rel = layer['albedo'] # относительный путь к карте albedo
            albedo_abs = os.path.abspath(os.path.join(current_path, albedo_rel)) # считаем абсолютнвй путь к карте albedo

            geometry_rel = layer['geometry'] # относительный путь к карте geometry
            geometry_abs = os.path.abspath(os.path.join(current_path, geometry_rel)) # считаем абсолютнвй путь к карте geometry
            
            new_layer = layers.add()
            
            new_layer.albedo = albedo_abs
            new_layer.geometry = geometry_abs
            new_layer.tint = layer['tint']['r'], layer['tint']['g'], layer['tint']['b'], layer['tint']['a']
            new_layer.exposure = layer['exposure']
            new_layer.smoothnessMultiplier = layer['smoothnessMultiplier']
            new_layer.metallic = layer['metallic']
        
        if group_parms == None:
            # Расположение новой ноды
            new_node_loc = find_new_node_location(active_tree)
            
            main_group_node.name = group_name
            main_group_node.label = group_name
            main_group_node.use_custom_color = True
            main_group_node.color = (0.176, 0, 0)
            main_group_node.location = new_node_loc
            main_group_node.width = 240
            main_group_node.node_tree = main_group_tree  # Привязываем созданное дерево группы
            main_group_node['mat_layers_data'] = matlayers_data
        
        else:
            main_group_node.name = group_parms['name']
            main_group_node.label = group_parms['label']
            main_group_node.use_custom_color = group_parms['use_custom_color']
            main_group_node.color = group_parms['color']
            main_group_node.location = group_parms['location']
            main_group_node.width = group_parms['width']
            main_group_node.node_tree = main_group_tree  # Привязываем созданное дерево группы
            main_group_node['mat_layers_data'] = matlayers_data
            
            
        # Добавляем входные/выходные ноды основной группы
        main_group_input = add_single_node(main_group_tree, 'NodeGroupInput', 0, 0)
        main_group_output = add_single_node(main_group_tree, 'NodeGroupOutput', 2000, 0)
        
        # Создаём входы и выходы основной группы
        main_group_input_menu_socket = main_group_tree.interface.new_socket(name='Layer ID', in_out='INPUT', socket_type='NodeSocketInt')
        main_group_input_uv_socket = main_group_tree.interface.new_socket(name='uv', in_out='INPUT', socket_type='NodeSocketVector')
        main_group_input_uv_socket.hide_value = True
        
        main_group_output_albedo_socket = main_group_tree.interface.new_socket(name='Albedo', in_out='OUTPUT', socket_type='NodeSocketColor')
        main_group_output_metallic_socket = main_group_tree.interface.new_socket(name='Metallic', in_out='OUTPUT', socket_type='NodeSocketFloat')
        main_group_output_roughness_socket = main_group_tree.interface.new_socket(name='Roughness', in_out='OUTPUT', socket_type='NodeSocketFloat')
        main_group_output_smoothness_socket = main_group_tree.interface.new_socket(name='Smoothness', in_out='OUTPUT', socket_type='NodeSocketFloat')
        main_group_output_normal_socket = main_group_tree.interface.new_socket(name='Normal', in_out='OUTPUT', socket_type='NodeSocketVector')
        main_group_output_height_socket = main_group_tree.interface.new_socket(name='Height', in_out='OUTPUT', socket_type='NodeSocketFloat')
        
        
        
        if group_parms != None:
            # восстанавливаем входные связи
            for node_socket, other_socket in group_parms["input_links"].items():
                node_socket = main_group_node.inputs[node_socket]
                active_tree.links.new(other_socket, node_socket)
            
            # восстанавливаем выходные связи
            for node_socket, other_socket in group_parms["output_links"].items():
                node_socket = main_group_node.outputs[node_socket]
                active_tree.links.new(other_socket, node_socket)
        
        main_group_node.shader_links.path = ml_path
        bpy.context.window_manager.temp_path = "" # очищаем временный путь для пустой строки
        
        
        
    ###===БЛОК СОЗДАНИЯ ГРУПП СО СЛОЯМИ===###
        def create_map_group(node_parms: dict,
                            base_group_tree: bpy.types.ShaderNodeTree,
                            layer_name: str,
                            output_type: str) -> bpy.types.NodeGroup:
            """
            Создает группу слоев определенного типа (напр: AlbedoLayersGroup, NormalLayersGroup...)
            
            :param node_parms: Параметры типа, цвета и позиции будущей ноды
            :param base_group_tree: Дерево, где будет располагаться нода (в нашем случае - дерево группы MatLayers)
            :param layer_name: Имя слоя (Albedo, Normal, Height и т.д.)
            :param output_type: Тип выхода (цвет, вектор и т.д.)
            """
            
            layer_name = layer_name.capitalize()
            layer_group_name = layer_name + 'LayersGroup'
            
            # Добавляем группу
            group_tree = bpy.data.node_groups.new(type='ShaderNodeTree', name=layer_group_name)
            
            # Добавляем ноду‑группу в целевой tree
            group_node = add_single_node(base_group_tree, 'ShaderNodeGroup', 0, 0)
            
            group_node.name = layer_group_name
            group_node.label = layer_group_name
            group_node.use_custom_color = True
            group_node.color = node_parms[layer_name][1]
            group_node.location = node_parms[layer_name][2]
            group_node.width = 240
            group_node.node_tree = group_tree  # Привязываем созданное дерево группы
            
            # Добавляем входные/выходные ноды albedo группы
            albedo_group_input = add_single_node(group_tree, 'NodeGroupInput', 0, 0)
            albedo_group_output = add_single_node(group_tree, 'NodeGroupOutput', 1000, 0)
            
            albedo_group_input_uv_socket = group_tree.interface.new_socket(name='uv', in_out='INPUT', socket_type='NodeSocketVector')
            
            # подключаем вход ноды albedo group связями
            base_group_tree.links.new(main_group_input.outputs['uv'], group_node.inputs['uv'])
            
            layers = main_group_node.shader_links.layers
            
        ###===БЛОК СОЗДАНИЯ СЛОЕВ===###
            ### ALBEDO
            if layer_name == 'Albedo':
                for i, layer in enumerate(layers):
                    numered_layer_name = layer_name+str(i)
                    group_output_socket = group_tree.interface.new_socket(name=f'Layer{i}', in_out='OUTPUT', socket_type=output_type)
                    
                    albedo_layer_node = add_single_node(group_tree, 'ShaderNodeTexImage', 300, 300 * -i)
                    
                    image, error = get_img_file(layer.albedo)
                    
                    albedo_layer_node.image = image
                    # albedo_layer_node.interpolation = 'Closest'
                    
                    group_tree.links.new(albedo_group_input.outputs['uv'], albedo_layer_node.inputs['Vector'])
                    
                    group_tree.links.new(albedo_layer_node.outputs['Color'], group_tree.nodes['Group Output'].inputs['Layer'+str(i)])
                    
            ### NORMAL
            elif layer_name == 'Normal':
                for i, layer in enumerate(layers):
                    numered_layer_name = layer_name+str(i)
                    group_output_socket = group_tree.interface.new_socket(name=f'Layer{i}', in_out='OUTPUT', socket_type=output_type)
                    
                    image_layer_node = add_single_node(group_tree, 'ShaderNodeTexImage', 300, 300 * -i)
                    
                    image, error = get_img_file(layer.geometry)
                    
                    image_layer_node.image = image
                    image_layer_node.image.colorspace_settings.name = 'Non-Color'
                    # image_layer_node.interpolation = 'Closest'
                    
                    separate_xyz_node = add_single_node(group_tree, 'ShaderNodeSeparateXYZ', 600, image_layer_node.location[1])
                    combine_xyz_node = add_single_node(group_tree, 'ShaderNodeCombineXYZ', 900, image_layer_node.location[1])
                    combine_xyz_node.inputs['Z'].default_value = 1.0
                    normal_map_node = add_single_node(group_tree, 'ShaderNodeNormalMap', 1200, image_layer_node.location[1])
                    normal_map_node.space = 'TANGENT'
                    normal_map_node.inputs[0].default_value = 1.0

                    group_tree.links.new(albedo_group_input.outputs['uv'], image_layer_node.inputs['Vector'])
                    group_tree.links.new(image_layer_node.outputs['Color'], separate_xyz_node.inputs['Vector'])
                    group_tree.links.new(separate_xyz_node.outputs['X'], combine_xyz_node.inputs['X'])
                    group_tree.links.new(separate_xyz_node.outputs['Y'], combine_xyz_node.inputs['Y'])
                    group_tree.links.new(combine_xyz_node.outputs['Vector'], normal_map_node.inputs['Color'])

                    group_tree.links.new(normal_map_node.outputs['Normal'], group_tree.nodes['Group Output'].inputs['Layer'+str(i)]) # ВЫВОД
                    
                    group_tree.nodes['Group Output'].location.x = normal_map_node.location.x + 300
                
            ### HEIGHT
            elif layer_name == 'Height':
                for i, layer in enumerate(layers):
                    numered_layer_name = layer_name+str(i)
                    group_output_socket = group_tree.interface.new_socket(name=f'Layer{i}', in_out='OUTPUT', socket_type=output_type)
                    
                    image_layer_node = add_single_node(group_tree, 'ShaderNodeTexImage', 300, 300 * -i)
                    
                    image, error = get_img_file(layer.geometry)
                    
                    image_layer_node.image = image
                    image_layer_node.image.colorspace_settings.name = 'Non-Color'
                    # image_layer_node.interpolation = 'Closest'
                    
                    separate_xyz_node = add_single_node(group_tree, 'ShaderNodeSeparateXYZ', 600, image_layer_node.location[1])
                    
                    group_tree.links.new(albedo_group_input.outputs['uv'], image_layer_node.inputs['Vector'])
                    
                    group_tree.links.new(image_layer_node.outputs['Color'], separate_xyz_node.inputs['Vector'])
                    group_tree.links.new(separate_xyz_node.outputs['Z'], group_tree.nodes['Group Output'].inputs['Layer'+str(i)])
                    
            ### TINT
            elif layer_name == 'Tint':
                for i, layer in enumerate(layers):
                    numered_layer_name = layer_name+str(i)
                    group_output_socket = group_tree.interface.new_socket(name=f'Layer{i}', in_out='OUTPUT', socket_type=output_type)
                    
                    tint_layer_node = add_single_node(group_tree, 'ShaderNodeRGB', 300, 300 * -i)
                    
                    tint_layer_node.outputs[0].default_value = layer.tint
                    
                    group_tree.links.new(tint_layer_node.outputs['Color'], group_tree.nodes['Group Output'].inputs['Layer'+str(i)])
                    
            ### EXPOSURE
            elif layer_name == 'Exposure':
                for i, layer in enumerate(layers):
                    numered_layer_name = layer_name+str(i)
                    group_output_socket = group_tree.interface.new_socket(name=f'Layer{i}', in_out='OUTPUT', socket_type=output_type)
                    
                    exposure_layer_node = add_single_node(group_tree, 'ShaderNodeValue', 300, 300 * -i)
                    exposure_layer_node.outputs[0].default_value = layer.exposure
                    
                    math_add_one_node = add_single_node(group_tree, 'ShaderNodeMath', 600, 300 * -i)
                    math_add_one_node.inputs[1].default_value = 1.0
                    
                    group_tree.links.new(exposure_layer_node.outputs['Value'], math_add_one_node.inputs[0])
                    group_tree.links.new(math_add_one_node.outputs[0], group_tree.nodes['Group Output'].inputs['Layer'+str(i)])
                    
            ### SMOOTHNESS
            elif layer_name == 'Smoothness':
                for i, layer in enumerate(layers):
                    numered_layer_name = layer_name+str(i)
                    group_output_socket = group_tree.interface.new_socket(name=f'Layer{i}', in_out='OUTPUT', socket_type=output_type)
                    
                    smoothness_layer_node = add_single_node(group_tree, 'ShaderNodeValue', 300, 300 * -i)
                    
                    smoothness_layer_node.outputs[0].default_value = layer.smoothnessMultiplier
                    
                    group_tree.links.new(smoothness_layer_node.outputs['Value'], group_tree.nodes['Group Output'].inputs['Layer'+str(i)])
                    
            ### METALLIC
            elif layer_name == 'Metallic':
                for i, layer in enumerate(layers):
                    numered_layer_name = layer_name+str(i)
                    group_output_socket = group_tree.interface.new_socket(name=f'Layer{i}', in_out='OUTPUT', socket_type=output_type)
                    
                    metallic_layer_node = add_single_node(group_tree, 'ShaderNodeValue', 300, 300 * -i)
                    
                    metallic_layer_node.outputs[0].default_value = layer.metallic
                    
                    group_tree.links.new(metallic_layer_node.outputs['Value'], group_tree.nodes['Group Output'].inputs['Layer'+str(i)])
                    
            return group_node
            
        node_parms = {
                        'Albedo': ['NodeSocketColor', (0.47, 0.5, 0.61), (900, 0)],
                        'Normal': ['NodeSocketVector', (0.38, 0.37, 0.59), (900, -300)],
                        'Height': ['NodeSocketFloat', (0.38, 0.32, 0.29), (900, -600)],
                        'Tint': ['NodeSocketColor', (0.42, 0.61, 0.43), (900, -900)],
                        'Exposure': ['NodeSocketFloat', (0.76, 0.77, 0.53), (900, -1200)],
                        'Smoothness': ['NodeSocketFloat', (0.61, 0.61, 0.61), (900, -1500)],
                        'Metallic': ['NodeSocketFloat', (0.42, 0.42, 0.42), (900, -1800)]
                        }
        
        ### ===БЛОК ДОБАВЛЕНИЯ СВИТЧЕРОВ===###
        def create_switcher_group(active_tree,
                                master_node,
                                group_name: str="SWITCHER"):
            """
            Создаем ноду-свитчер, всю ее внутреннюю структуру и связи
            
            :param active_tree: Дерево, в котором создается нода (в данном случае - дерево внутри ноды MatLayers)
            :param master_node: Нода, чьи выходы мы будем выбирать данным свитчером
            :param group_name: Будущее имя текущей ноды-свитчера
            """
            
            if not active_tree:
                print("Ошибка: active_tree не указан")
                return None
                
            main_group_tree = bpy.data.node_groups.new(type='ShaderNodeTree', name=group_name)
            
            # Добавляем ноду‑группу в целевой tree
            switcher_node = add_single_node(active_tree, 'ShaderNodeGroup', 0, 0)
            
            # Параметры ноды
            switcher_node.name = group_name
            switcher_node.label = group_name + '_albedo'
            switcher_node.use_custom_color = True
            switcher_node.color = (0.28, 0.2, 0.3)
            switcher_node.location = master_node.location + Vector((300.0, 0.0))
            switcher_node.width = 140
            switcher_node.node_tree = main_group_tree  # Привязываем созданное дерево группы
            
            # Добавляем входные/выходные ноды albedo группы
            switcher_group_input = add_single_node(main_group_tree, 'NodeGroupInput', 0, 0)
            switcher_group_output = add_single_node(main_group_tree, 'NodeGroupOutput', 1200, 0)
            
            switcher_group_input_id_socket = main_group_tree.interface.new_socket(name='Layer ID', in_out='INPUT', socket_type='NodeSocketInt')
            
            # Создаем выходы групп
            switcher_group_output_socket = main_group_tree.interface.new_socket(name='result', in_out='OUTPUT', socket_type='NodeSocketColor')
            
            # соединяем сокеты меню
            input_node = active_tree.nodes.get('Group Input')
            menu_input = input_node.outputs['Layer ID']
            active_tree.links.new(menu_input, switcher_node.inputs['Layer ID'])
            
            layers_count = 0

            for i, layer in enumerate(master_node.outputs):
                layers_count += 1
                switcher_group_input_layer_socket = main_group_tree.interface.new_socket(name=f'Layer{i}', in_out='INPUT', socket_type='NodeSocketColor')
                
                set_socket_value(switcher_node, layer.name, (1.0, 0.0, 0.0, 1.0))
                
                # подключаем вход ноды
                active_tree.links.new(master_node.outputs[master_node.outputs[i].name], switcher_node.inputs[i+1])
            
            switcher_node_tree = switcher_node.node_tree

            mix_color_nodes_list = []
            add_color_nodes_list = []
            i = 0
            for output in switcher_group_input.outputs:
                if output.name == 'Layer ID' or output.name == '':
                    continue

                y_loc = i*-230

                compare_node = add_single_node(switcher_node_tree, 'ShaderNodeMath', 300, y_loc)
                compare_node.operation = 'COMPARE'
                compare_node.inputs[1].default_value = i

                mix_color_node = add_single_node(switcher_node_tree, 'ShaderNodeMix', 600, y_loc)
                mix_color_node.data_type = 'RGBA'
                mix_color_node.inputs['A'].default_value = [0.0, 0.0, 0.0, 0.0]
                mix_color_nodes_list.append(mix_color_node)

                switcher_node_tree.links.new(switcher_group_input.outputs['Layer ID'], compare_node.inputs[0])
                switcher_node_tree.links.new(switcher_group_input.outputs[f'Layer{i}'], mix_color_node.inputs['B'])
                switcher_node_tree.links.new(compare_node.outputs[0], mix_color_node.inputs['Factor'])

                if i<(layers_count-1): # Чтобы создать на одну ноду add_color_node меньше
                    add_color_node = add_single_node(switcher_node_tree, 'ShaderNodeMix', 900 + i*300, y_loc)
                    add_color_node.data_type = 'RGBA'
                    add_color_node.blend_type = 'ADD'
                    add_color_node.inputs['Factor'].default_value = 1.0
                    add_color_nodes_list.append(add_color_node)

                    # Сдвигаем выходную ноду правее всех нод
                    switcher_group_output.location = [add_color_node.location[0] + 300, switcher_group_output.location[1]]
                i+=1
            
            for i, mix_node in enumerate(mix_color_nodes_list):
                if i==0:
                    switcher_node_tree.links.new(mix_node.outputs['Result'], add_color_nodes_list[i].inputs['A'])
                elif i>0 and i<len(add_color_nodes_list):
                    switcher_node_tree.links.new(add_color_nodes_list[i-1].outputs['Result'], add_color_nodes_list[i].inputs['A'])
                    switcher_node_tree.links.new(mix_node.outputs['Result'], add_color_nodes_list[i-1].inputs['B'])
                elif i==len(add_color_nodes_list):
                    switcher_node_tree.links.new(mix_node.outputs['Result'], add_color_nodes_list[i-1].inputs['B'])


            switcher_node_tree.links.new(add_color_nodes_list[-1].outputs['Result'], switcher_group_output.inputs[0]) # ВЫВОД
            
            return switcher_node
            
        # исполняем методы
        for layer_name in node_parms:
            socket_type = node_parms[layer_name][0]
            layer_name = layer_name.lower()
            map_group = create_map_group(node_parms, main_group_tree, layer_name, socket_type)
            
            if map_group == {'CANCELLED'}:
                return {'CANCELLED'}
            
            switchers = []
            
            if not "SWITCHER" in main_group_tree.nodes:
                switcher_group = create_switcher_group(main_group_tree, map_group, "SWITCHER")
                switchers.append(switcher_group)
            else:
                switcher_group = main_group_tree.nodes["SWITCHER"]
                switcher_group_tree = switcher_group.node_tree
                
                switcher_group_copy = add_single_node(main_group_tree, 'ShaderNodeGroup', 0, 0)
                
                switcher_group_copy.name = "SWITCHER"
                switcher_group_copy.label = "SWITCHER" + "_" + layer_name
                switcher_group_copy.use_custom_color = True
                switcher_group_copy.color = (0.28, 0.2, 0.3)
                switcher_group_copy.location = map_group.location + Vector((300.0, 0.0))
                switcher_group_copy.width = 140
                switcher_group_copy.node_tree = switcher_group_tree
                
                main_group_tree.links.new(main_group_tree.nodes['Group Input'].outputs[0], switcher_group_copy.inputs[0])
                
                
                for i, input in enumerate(switcher_group.inputs):
                    if i < switcher_group_copy.inputs.__len__() - 1:
                        main_group_tree.links.new(map_group.outputs[i], switcher_group_copy.inputs[i+1])
                
                switcher_group_copy.update()
                switchers.append(switcher_group_copy)
                
            def connect_switcher2output(switchers, output):
                if switchers == []:
                    return
                
                for switcher in switchers:
                    switcher_type = layer_name.title()
                    switcher_output = switcher.outputs[0]
                    
                    if switcher_type in output.inputs:
                        main_group_tree.links.new(switcher_output, output.inputs[switcher_type])
                    
                    if switcher_type == "Smoothness":
                        invert_node = add_single_node(main_group_tree, 'ShaderNodeMath', 0, 0)
                        invert_node.operation = 'SUBTRACT'
                        invert_node.inputs[0].default_value = 1
                        invert_node.location = [switcher.location[0] + 300, switcher.location[1]]

                        main_group_tree.links.new(switcher_output, invert_node.inputs[1])
                        main_group_tree.links.new(invert_node.outputs['Value'], output.inputs['Roughness'])
                return
                
            connect_switcher2output(switchers, main_group_output)
            
        def add_albedo_tint_exposure_mixer(main_group_tree):
            albedo_switcher_node = None
            tint_switcher_node = None
            exposure_switcher_node = None
            
            for node in main_group_tree.nodes:
                if node.label == 'SWITCHER_albedo':
                    albedo_switcher_node = node
                elif node.label == 'SWITCHER_tint':
                    tint_switcher_node = node
                elif node.label == 'SWITCHER_exposure':
                    exposure_switcher_node = node
                    
            main_group_output = main_group_tree.nodes['Group Output']
            
            # Находим существующий линк
            existing_link = None
            for link in main_group_tree.links:
                if link.from_node.label == 'SWITCHER_albedo' and link.to_node.name == 'Group Output':
                    existing_link = link
                    break
                    
            if existing_link:
                mixer_group_node = main_group_tree.nodes.new('ShaderNodeGroup')
                mixer_group_node.location = (
                    (existing_link.from_node.location.x + existing_link.to_node.location.x) / 2,
                    (existing_link.from_node.location.y + existing_link.to_node.location.y) / 2
                )
                
                mixer_group_node.name = "Mixer Group"
                mixer_group_node.label = "Mixer Group"
                mixer_group_node.use_custom_color = True
                mixer_group_node.color = (0.6, 0.5, 0.5)
                mixer_group_node.width = 140
                
                # Новое дерево нод
                mixer_group_tree = bpy.data.node_groups.new(type='ShaderNodeTree', name='mixer_group_tree')
                mixer_group_node.node_tree = mixer_group_tree
                
                # Создаем новые входный и выходные сокеты
                mixer_albedo_input = mixer_group_tree.interface.new_socket(name='Albedo', in_out='INPUT', socket_type='NodeSocketColor')
                mixer_tint_input = mixer_group_tree.interface.new_socket(name='Tint', in_out='INPUT', socket_type='NodeSocketColor')
                mixer_exposure_input = mixer_group_tree.interface.new_socket(name='Exposure', in_out='INPUT', socket_type='NodeSocketFloat')
                mixer_result_output = mixer_group_tree.interface.new_socket(name='result', in_out='OUTPUT', socket_type='NodeSocketColor')
                set_socket_value(mixer_group_node, 'Albedo', (1.0, 1.0, 1.0, 1.0))
                set_socket_value(mixer_group_node, 'Tint', (1.0, 1.0, 1.0, 1.0))
                set_socket_value(mixer_group_node, 'Exposure', 1.0)
                
                # Удаляем старый линк
                main_group_tree.links.remove(existing_link)
                
                # Пробрасываем новые линки
                main_group_tree.links.new(albedo_switcher_node.outputs['result'], mixer_group_node.inputs['Albedo'])
                main_group_tree.links.new(tint_switcher_node.outputs['result'], mixer_group_node.inputs['Tint'])
                main_group_tree.links.new(exposure_switcher_node.outputs['result'], mixer_group_node.inputs['Exposure'])
                main_group_tree.links.new(mixer_group_node.outputs['result'], main_group_output.inputs['Albedo'])
                
                
                ### СОЗДАЕМ СТРУКТУРУ ВНУТРИ МИКСЕРА
                mixer_input_node = add_single_node(mixer_group_tree, 'NodeGroupInput', 0, 0)
                mixer_output_node = add_single_node(mixer_group_tree, 'NodeGroupOutput', 900, 0)
                tint_multiply_node = add_single_node(mixer_group_tree, 'ShaderNodeMix', 300, 0)
                exposure_multiply_node = add_single_node(mixer_group_tree, 'ShaderNodeMix', 600, 0)
                tint_multiply_node.data_type = 'RGBA'
                exposure_multiply_node.data_type = 'RGBA'
                tint_multiply_node.blend_type = 'MULTIPLY'
                exposure_multiply_node.blend_type = 'MULTIPLY'
                tint_multiply_node.inputs['Factor'].default_value = 1.0
                exposure_multiply_node.inputs['Factor'].default_value = 1.0
                tint_multiply_node.inputs['A'].name = 'Albedo'
                exposure_multiply_node.inputs['A'].name = 'Albedo'
                tint_multiply_node.inputs['B'].name = 'Tint'
                exposure_multiply_node.inputs['B'].name = 'Exposure'
                
                # Пробрасываем линки
                mixer_group_tree.links.new(mixer_input_node.outputs['Albedo'], tint_multiply_node.inputs['Albedo'])
                mixer_group_tree.links.new(mixer_input_node.outputs['Tint'], tint_multiply_node.inputs['Tint'])
                mixer_group_tree.links.new(tint_multiply_node.outputs['Result'], exposure_multiply_node.inputs['Albedo'])
                mixer_group_tree.links.new(mixer_input_node.outputs['Exposure'], exposure_multiply_node.inputs['Exposure'])
                mixer_group_tree.links.new(exposure_multiply_node.outputs['Result'], mixer_output_node.inputs['result'])
                
        add_albedo_tint_exposure_mixer(main_group_tree)
        
        # задаем дефолтное значение для меню
        if len(matlayers_data) > 0:
            main_group_node.inputs[0].default_value = 0
        
        # делаем ноду активной
        active_tree.nodes.active = main_group_node
        # bpy.context.view_layer.objects.active.select_set(True) # Оставил, вдруг понадобится
        
def def_mat_layers_node() -> bool:
    """
    Определяем, является ли активная нода MatLayers нодой
    """
    
    active_node = get_active_node(get_active_tree())
    is_mat_layers_node = False
    
    if active_node:
        if active_node.type == "GROUP":
            if "mat_layers_data" in active_node:
                is_mat_layers_node = True
    
    return is_mat_layers_node

def add_node(group_name="Mat Layers", node_parms=None, ml_path=""): # TODO ВЕРОЯТНО, ПРОВЕРКА НЕ НУЖНА
    """
    Создаем новую MatLayers ноду при выборе MatLayers или MatLayers~ файла
    
    :param group_name: Будущее имя новой MatLayers ноды
    :param node_parms: Параметры будущей ноды, взятые либо из MatLayers файла, либо из старой ноды при замене
    :param ml_path: путь до текущего MatLayers файла
    """

    active_tree = get_active_tree()
    is_mat_layers_node = def_mat_layers_node()
    
    # если активная нода - это mat_layers, заменяем ее
    if is_mat_layers_node:
        print(f"Update selected Node")
        active_node = get_active_node(active_tree)
        ml_path = active_node.shader_links.path
    else: # если это НЕ mat_layers, создаем ноду с нуля
        print(f"Create new Mat Layers Node")
        
        matlayers_data = get_matlayers_data(ml_path)
        matlayers_layers = matlayers_data['layers']
        file_path = get_matlayers_path(ml_path)
        
        construct_group_node(active_tree, matlayers_data, None, ml_path=ml_path)