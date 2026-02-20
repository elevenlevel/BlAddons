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
        img.alpha_mode = 'CHANNEL_PACKED'
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
            new_layer.smoothness_multiplier = layer['smoothnessMultiplier']
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
        main_group_input_menu_socket = main_group_tree.interface.new_socket(name='LAYER ID', in_out='INPUT', socket_type='NodeSocketInt')
        main_group_input_uv_socket = main_group_tree.interface.new_socket(name='uv', in_out='INPUT', socket_type='NodeSocketVector')
        main_group_input_uv_socket.hide_value = True
        
        main_group_output_albedo_rgb_socket = main_group_tree.interface.new_socket(name='ALBEDO_RGB', in_out='OUTPUT', socket_type='NodeSocketColor')
        main_group_output_albedo_a_socket = main_group_tree.interface.new_socket(name='ALBEDO_A', in_out='OUTPUT', socket_type='NodeSocketFloat')
        main_group_output_geometry_xyz_socket = main_group_tree.interface.new_socket(name='GEOMETRY_XYZ', in_out='OUTPUT', socket_type='NodeSocketColor')
        main_group_output_geometry_a_socket = main_group_tree.interface.new_socket(name='GEOMETRY_A', in_out='OUTPUT', socket_type='NodeSocketFloat')
        main_group_output_smoothness_multiplier_socket = main_group_tree.interface.new_socket(name='SMOOTHNESS_MULTIPLIER', in_out='OUTPUT', socket_type='NodeSocketFloat')
        main_group_output_metallic_socket = main_group_tree.interface.new_socket(name='METALLIC', in_out='OUTPUT', socket_type='NodeSocketFloat')
        
        
        
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
            Создает группу слоев определенного типа (напр: AlbedoLayersGroup, GeometryLayersGroup...)
            
            :param node_parms: Параметры типа, цвета и позиции будущей ноды
            :param base_group_tree: Дерево, где будет располагаться нода (в нашем случае - дерево группы MatLayers)
            :param layer_name: Имя слоя (Albedo, Geometry и т.д.)
            :param output_type: Тип выхода (цвет, вектор и т.д.)
            """

            layer_group_name = layer_name + '_LAYERS_GROUP'
            
            # Добавляем группу
            group_tree = bpy.data.node_groups.new(type='ShaderNodeTree', name=layer_group_name)
            
            # Добавляем ноду‑группу в целевой tree
            group_node = add_single_node(base_group_tree, 'ShaderNodeGroup', 0, 0)
            
            group_node.name = layer_group_name
            group_node.label = layer_group_name
            group_node.use_custom_color = True
            group_node.color = node_parms[layer_name.upper()][1]
            group_node.location = node_parms[layer_name.upper()][2]
            group_node.width = 240
            group_node.node_tree = group_tree  # Привязываем созданное дерево группы
            
            # Добавляем входные/выходные ноды albedo группы
            current_group_input = add_single_node(group_tree, 'NodeGroupInput', 0, 0)
            current_group_output = add_single_node(group_tree, 'NodeGroupOutput', 1000, 0)
            
            layers = main_group_node.shader_links.layers
            
        ###===БЛОК СОЗДАНИЯ СЛОЕВ===###
            outputs_list = {}

            ### ALBEDO
            if layer_name == 'ALBEDO':
                albedo_rgb_outputs, albedo_a_outputs = [], []

                # Добавляем входной сокет uv
                current_group_input_uv_socket = group_tree.interface.new_socket(name='uv', in_out='INPUT', socket_type='NodeSocketVector')

                for i, layer in enumerate(layers):
                    numered_layer_name = layer_name+str(i)

                    output0_name = f'ALBEDO_RGB_LAYER{i}'
                    output1_name = f'ALBEDO_A_LAYER{i}'

                    albedo_output_socket = group_tree.interface.new_socket(name=output0_name, in_out='OUTPUT', socket_type=output_type)
                    smoothness_output_socket = group_tree.interface.new_socket(name=output1_name, in_out='OUTPUT', socket_type='NodeSocketFloat')
                    
                    albedo_rgb_outputs.append(albedo_output_socket)
                    albedo_a_outputs.append(smoothness_output_socket)
                    
                    albedo_layer_node = add_single_node(group_tree, 'ShaderNodeTexImage', 300, 300 * -i)
                    
                    image, error = get_img_file(layer.albedo)
                    
                    albedo_layer_node.image = image
                    
                    group_tree.links.new(current_group_input.outputs['uv'], albedo_layer_node.inputs['Vector'])
                    
                    group_tree.links.new(albedo_layer_node.outputs['Color'], group_tree.nodes['Group Output'].inputs[output0_name])
                    group_tree.links.new(albedo_layer_node.outputs['Alpha'], group_tree.nodes['Group Output'].inputs[output1_name])
                
                outputs_list['ALBEDO_RGB'] = albedo_rgb_outputs
                outputs_list['ALBEDO_A'] = albedo_a_outputs
                
                # подключаем вход ноды albedo group связями
                base_group_tree.links.new(main_group_input.outputs['uv'], group_node.inputs['uv'])
            
            ### GEOMETRY
            elif layer_name == 'GEOMETRY':
                geometry_xyz_outputs, geometry_a_outputs = [], []

                # Добавляем входной сокет uv
                current_group_input_uv_socket = group_tree.interface.new_socket(name='uv', in_out='INPUT', socket_type='NodeSocketVector')
                
                for i, layer in enumerate(layers):
                    numered_layer_name = layer_name+str(i)

                    output0_name = f'GEOMERY_XYZ_LAYER{i}'
                    output1_name = f'GEOMETRY_A_LAYER{i}'

                    geometry_xyz_output_socket = group_tree.interface.new_socket(name=output0_name, in_out='OUTPUT', socket_type=output_type)
                    geometry_a_output_socket = group_tree.interface.new_socket(name=output1_name, in_out='OUTPUT', socket_type='NodeSocketFloat')
                    
                    geometry_xyz_outputs.append(geometry_xyz_output_socket)
                    geometry_a_outputs.append(geometry_a_output_socket)
                    
                    image_layer_node = add_single_node(group_tree, 'ShaderNodeTexImage', 300, 300 * -i)
                    
                    image, error = get_img_file(layer.geometry)
                    
                    image_layer_node.image = image
                    image_layer_node.image.colorspace_settings.name = 'Non-Color'
                
                    group_tree.links.new(current_group_input.outputs['uv'], image_layer_node.inputs['Vector']) # ВВОД
                    group_tree.links.new(image_layer_node.outputs['Color'], group_tree.nodes['Group Output'].inputs[output0_name]) # ВЫВОД
                    group_tree.links.new(image_layer_node.outputs['Alpha'], group_tree.nodes['Group Output'].inputs[output1_name]) # ВЫВОД
                
                outputs_list['GEOMETRY_XYZ'] = geometry_xyz_outputs
                outputs_list['GEOMETRY_A'] = geometry_a_outputs
                
                # подключаем вход ноды albedo group связями
                base_group_tree.links.new(main_group_input.outputs['uv'], group_node.inputs['uv'])

            ### TINT
            elif layer_name == 'TINT':
                tint_outputs = []

                for i, layer in enumerate(layers):
                    numered_layer_name = layer_name+str(i)

                    group_output_socket = group_tree.interface.new_socket(name=f'LAYER{i}', in_out='OUTPUT', socket_type=output_type)
                    tint_outputs.append(group_output_socket)
                    
                    tint_layer_node = add_single_node(group_tree, 'ShaderNodeRGB', 300, 300 * -i)
                    
                    tint_layer_node.outputs[0].default_value = layer.tint
                    
                    group_tree.links.new(tint_layer_node.outputs['Color'], group_tree.nodes['Group Output'].inputs['LAYER'+str(i)])
                
                outputs_list['TINT'] = tint_outputs
                
            ### EXPOSURE
            elif layer_name == 'EXPOSURE':
                exposure_outputs = []
                for i, layer in enumerate(layers):
                    numered_layer_name = layer_name+str(i)

                    group_output_socket = group_tree.interface.new_socket(name=f'LAYER{i}', in_out='OUTPUT', socket_type=output_type)
                    exposure_outputs.append(group_output_socket)
                    
                    exposure_layer_node = add_single_node(group_tree, 'ShaderNodeValue', 300, 300 * -i)
                    exposure_layer_node.outputs[0].default_value = layer.exposure
                    
                    math_add_one_node = add_single_node(group_tree, 'ShaderNodeMath', 600, 300 * -i)
                    math_add_one_node.inputs[1].default_value = 1.0
                    
                    group_tree.links.new(exposure_layer_node.outputs['Value'], math_add_one_node.inputs[0])
                    group_tree.links.new(math_add_one_node.outputs[0], group_tree.nodes['Group Output'].inputs['LAYER'+str(i)])
                
                outputs_list['EXPOSURE'] = exposure_outputs

            ### SMOOTHNESS_MULTIPLIER
            elif layer_name == 'SMOOTHNESS_MULTIPLIER':
                smoothness_multiplier_outputs = []

                for i, layer in enumerate(layers):
                    numered_layer_name = layer_name+str(i)

                    group_output_socket = group_tree.interface.new_socket(name=f'LAYER{i}', in_out='OUTPUT', socket_type=output_type)
                    smoothness_multiplier_outputs.append(group_output_socket)
                    
                    smoothness_multiplier_layer_node = add_single_node(group_tree, 'ShaderNodeValue', 300, 300 * -i)
                    
                    smoothness_multiplier_layer_node.outputs[0].default_value = layer.smoothness_multiplier
                    
                    group_tree.links.new(smoothness_multiplier_layer_node.outputs['Value'], group_tree.nodes['Group Output'].inputs['LAYER'+str(i)])

                outputs_list['SMOOTHNESS_MULTIPLIER'] = smoothness_multiplier_outputs
            
            ### METALLIC
            elif layer_name == 'METALLIC':
                metallic_outputs = []

                for i, layer in enumerate(layers):
                    numered_layer_name = layer_name+str(i)
                    
                    group_output_socket = group_tree.interface.new_socket(name=f'LAYER{i}', in_out='OUTPUT', socket_type=output_type)
                    metallic_outputs.append(group_output_socket)
                    
                    metallic_layer_node = add_single_node(group_tree, 'ShaderNodeValue', 300, 300 * -i)
                    
                    metallic_layer_node.outputs[0].default_value = layer.metallic
                    
                    group_tree.links.new(metallic_layer_node.outputs['Value'], group_tree.nodes['Group Output'].inputs['LAYER'+str(i)])
                
                outputs_list['METALLIC'] = metallic_outputs
                
            return group_node, outputs_list
            
        node_parms = {
                        'ALBEDO': ['NodeSocketColor', (0.47, 0.5, 0.61), (900, 0)],
                        'GEOMETRY': ['NodeSocketVector', (0.38, 0.37, 0.59), (900, -300)],
                        'TINT': ['NodeSocketColor', (0.42, 0.61, 0.43), (900, -600)],
                        'EXPOSURE': ['NodeSocketFloat', (0.76, 0.77, 0.53), (900, -900)],
                        'SMOOTHNESS_MULTIPLIER': ['NodeSocketFloat', (0.61, 0.61, 0.61), (900, -1200)],
                        'METALLIC': ['NodeSocketFloat', (0.42, 0.42, 0.42), (900, -1500)]
                        }
        
        ### ===БЛОК ДОБАВЛЕНИЯ СВИТЧЕРОВ===###
        def create_switcher_group(active_tree,
                                master_node,
                                tree_name: str="SWITCHER",
                                group_type: str="ALBEDO",
                                parent_outputs: dict=None):
            """
            Создаем ноду-свитчер, всю ее внутреннюю структуру и связи
            
            :param active_tree: Дерево, в котором создается нода (в данном случае - дерево внутри ноды MatLayers)
            :param master_node: Нода, чьи выходы мы будем выбирать данным свитчером
            :param group_name: Будущее имя текущей ноды-свитчера
            """

            group_name = f'SWITCHER_{group_type}'
            
            if not active_tree:
                print("Ошибка: active_tree не указан")
                return None
            
            main_group_tree = bpy.data.node_groups.new(type='ShaderNodeTree', name=tree_name)
            
            # Добавляем ноду‑группу в целевой tree
            switcher_node = add_single_node(active_tree, 'ShaderNodeGroup', 0, 0)
            
            # Параметры ноды
            switcher_node.name = group_type
            switcher_node.label = group_name
            switcher_node.use_custom_color = True
            switcher_node.color = (0.28, 0.2, 0.3)
            switcher_node.location = master_node.location + Vector((600.0, 0.0))
            switcher_node.width = 140
            switcher_node.node_tree = main_group_tree  # Привязываем созданное дерево группы
            switcher_node.hide = True
            
            # Добавляем входные/выходные ноды albedo группы
            switcher_group_input = add_single_node(main_group_tree, 'NodeGroupInput', 0, 0)
            switcher_group_output = add_single_node(main_group_tree, 'NodeGroupOutput', 1200, 0)
            
            switcher_group_input_id_socket = main_group_tree.interface.new_socket(name='LAYER ID', in_out='INPUT', socket_type='NodeSocketInt')
            
            # Создаем выходы групп
            switcher_group_output_socket = main_group_tree.interface.new_socket(name='RESULT', in_out='OUTPUT', socket_type='NodeSocketColor')
            
            # соединяем сокеты меню
            input_node = active_tree.nodes.get('Group Input')
            menu_input = input_node.outputs['LAYER ID']
            active_tree.links.new(menu_input, switcher_node.inputs['LAYER ID'])
            
            layers_count = 0
            
            # создаем входы по количеству слоев ноды LAYERS
            for i, layer in enumerate(parent_outputs):
                layers_count += 1
                switcher_group_input_layer_socket = main_group_tree.interface.new_socket(name=f'LAYER{i}', in_out='INPUT', socket_type='NodeSocketColor')
                
                set_socket_value(switcher_node, layer.name, (1.0, 0.0, 0.0, 1.0))
            
            switcher_node_tree = switcher_node.node_tree

            compare_nodes_list = []
            add_vector_nodes_list = []
            i = 0
            
            for output in switcher_group_input.outputs:
                if output.name == 'LAYER ID' or output.name == '':
                    continue

                y_loc = i*-230

                compare_node = add_single_node(switcher_node_tree, 'ShaderNodeMath', 300, y_loc)
                compare_node.use_clamp = False
                compare_node.operation = 'COMPARE'
                compare_node.inputs[-1].default_value = 0.5
                compare_node.inputs[1].default_value = i

                multiply_layer_compare_node = add_single_node(switcher_node_tree, 'ShaderNodeVectorMath', 600, y_loc)
                multiply_layer_compare_node.operation = 'MULTIPLY'
                compare_nodes_list.append(multiply_layer_compare_node) # ЗАЧЕМ ЭТО???

                switcher_node_tree.links.new(switcher_group_input.outputs['LAYER ID'], compare_node.inputs[0])
                switcher_node_tree.links.new(switcher_group_input.outputs[f'LAYER{i}'], multiply_layer_compare_node.inputs[0])
                switcher_node_tree.links.new(compare_node.outputs[0], multiply_layer_compare_node.inputs[1])

                if i<(layers_count-1): # Чтобы создать на одну ноду add_color_node меньше
                    add_vector_node = add_single_node(switcher_node_tree, 'ShaderNodeVectorMath', 900 + i*300, y_loc)
                    add_vector_node.operation = 'ADD'
                    add_vector_nodes_list.append(add_vector_node)

                    # Сдвигаем выходную ноду правее всех нод
                    switcher_group_output.location = [add_vector_node.location[0] + 300, switcher_group_output.location[1]]
                i+=1
            
            for i, mix_node in enumerate(compare_nodes_list):
                if i==0:
                    switcher_node_tree.links.new(mix_node.outputs[0], add_vector_nodes_list[i].inputs[0])
                elif i>0 and i<len(add_vector_nodes_list):
                    switcher_node_tree.links.new(add_vector_nodes_list[i-1].outputs[0], add_vector_nodes_list[i].inputs[0])
                    switcher_node_tree.links.new(mix_node.outputs[0], add_vector_nodes_list[i-1].inputs[1])
                elif i==len(add_vector_nodes_list):
                    switcher_node_tree.links.new(mix_node.outputs[0], add_vector_nodes_list[i-1].inputs[1])


            switcher_node_tree.links.new(add_vector_nodes_list[-1].outputs[0], switcher_group_output.inputs[0]) # ВЫВОД
            
            return switcher_node
        
        # исполняем методы
        first_switcher = None
        last_switcher = None
        last_layers_node = None

        for layer_name in node_parms:
            socket_type = node_parms[layer_name][0]

            map_group, outputs_list = create_map_group(node_parms, main_group_tree, layer_name, socket_type)
            
            # дополнительно ранжируем layers ноды по вертикали
            if last_layers_node != None:
                map_group.location[1] = last_layers_node.location[1] - (len(map_group.outputs) * 30)
            last_layers_node = map_group
            
            if map_group == {'CANCELLED'}:
                return {'CANCELLED'}
            
            switchers = []

            for key, value in outputs_list.items():
                if first_switcher == None:
                    iter = 0

                    
                    parent_outputs = value

                    '''
                    socket_type = parent_outputs[0].socket_type
                    
                    if socket_type == 'NodeSocketColor' or socket_type == 'NodeSocketVector':
                        data_type = 'COLOR'
                    else:
                        data_type = 'FLOAT'
                    '''

                    first_switcher = create_switcher_group(main_group_tree, map_group, "SWITCHER", key, parent_outputs)
                    first_switcher.location.y -= iter * 100
                    
                    switchers.append(first_switcher)
                    
                    last_switcher = first_switcher

                    iter += 1
                else:
                    if first_switcher == None:
                        return
                    
                    first_switcher_copy = add_single_node(main_group_tree, 'ShaderNodeGroup', 0, 0)
                    
                    first_switcher_copy.name = key
                    first_switcher_copy.label = "SWITCHER" + "_" + key
                    first_switcher_copy.use_custom_color = True
                    first_switcher_copy.color = (0.16, 0.18, 0.28)
                    first_switcher_copy.location = Vector((map_group.location[0] + 600.0, last_switcher.location[1] - 100.0))
                    first_switcher_copy.width = 140
                    first_switcher_copy.node_tree = first_switcher.node_tree
                    first_switcher_copy.hide = True
                    
                    # подключаем ID из главного входа
                    main_group_tree.links.new(main_group_tree.nodes['Group Input'].outputs[0], first_switcher_copy.inputs[0])
                    
                    switchers.append(first_switcher_copy)

                    last_switcher = first_switcher_copy
                
                # пробрасываем линки между нодой LAYERS и нодой SWITCHER
                for i, input in enumerate(value):
                    main_group_tree.links.new(map_group.outputs[input.name], last_switcher.inputs[i+1])

            
            def connect_switcher2output(switchers, output):
                if switchers == []:
                    return
                
                for switcher in switchers:
                    switcher_type = switcher.name
                    switcher_output = switcher.outputs[0]

                    if switcher_type in output.inputs:
                        main_group_tree.links.new(switcher_output, output.inputs[switcher_type])
                return
                
            connect_switcher2output(switchers, main_group_output)
            
        def add_albedo_tint_exposure_mixer(main_group_tree):
            albedo_switcher_node = None
            tint_switcher_node = None
            exposure_switcher_node = None
            
            for node in main_group_tree.nodes:
                if node.label == 'SWITCHER_ALBEDO_RGB':
                    albedo_switcher_node = node
                elif node.label == 'SWITCHER_TINT':
                    tint_switcher_node = node
                elif node.label == 'SWITCHER_EXPOSURE':
                    exposure_switcher_node = node
                    
            main_group_output = main_group_tree.nodes['Group Output']
            
            # Находим существующий линк
            existing_link = None
            for link in main_group_tree.links:
                if link.from_node.label == 'SWITCHER_ALBEDO_RGB' and link.to_node.name == 'Group Output':
                    existing_link = link
                    break
                    
            if existing_link:
                mixer_group_node = main_group_tree.nodes.new('ShaderNodeGroup')
                mixer_group_node.location = (
                    (existing_link.from_node.location.x + existing_link.to_node.location.x) / 2,
                    (existing_link.from_node.location.y + existing_link.to_node.location.y) / 2
                )
                
                mixer_group_node.name = "MIXER_GROUP"
                mixer_group_node.label = "MIXER_GROUP"
                mixer_group_node.use_custom_color = True
                mixer_group_node.color = (0.4, 0.6, 0.5)
                mixer_group_node.width = 140
                
                # Новое дерево нод
                mixer_group_tree = bpy.data.node_groups.new(type='ShaderNodeTree', name='mixer_group_tree')
                mixer_group_node.node_tree = mixer_group_tree
                
                # Создаем новые входный и выходные сокеты
                mixer_albedo_input = mixer_group_tree.interface.new_socket(name='ALBEDO_RGB', in_out='INPUT', socket_type='NodeSocketColor')
                mixer_tint_input = mixer_group_tree.interface.new_socket(name='TINT', in_out='INPUT', socket_type='NodeSocketColor')
                mixer_exposure_input = mixer_group_tree.interface.new_socket(name='EXPOSURE', in_out='INPUT', socket_type='NodeSocketFloat')

                mixer_albedo_output = mixer_group_tree.interface.new_socket(name='ALBEDO_RGB', in_out='OUTPUT', socket_type='NodeSocketColor')
                
                set_socket_value(mixer_group_node, 'ALBEDO_RGB', (1.0, 1.0, 1.0, 1.0))
                set_socket_value(mixer_group_node, 'TINT', (1.0, 1.0, 1.0, 1.0))
                set_socket_value(mixer_group_node, 'EXPOSURE', 1.0)
                
                # Удаляем старый линк
                main_group_tree.links.remove(existing_link)
                
                # Пробрасываем новые линки
                main_group_tree.links.new(albedo_switcher_node.outputs['RESULT'], mixer_group_node.inputs['ALBEDO_RGB'])
                main_group_tree.links.new(tint_switcher_node.outputs['RESULT'], mixer_group_node.inputs['TINT'])
                main_group_tree.links.new(exposure_switcher_node.outputs['RESULT'], mixer_group_node.inputs['EXPOSURE'])

                main_group_tree.links.new(mixer_group_node.outputs['ALBEDO_RGB'], main_group_output.inputs['ALBEDO_RGB'])
                
                ### СОЗДАЕМ СТРУКТУРУ ВНУТРИ МИКСЕРА
                mixer_input_node = add_single_node(mixer_group_tree, 'NodeGroupInput', 0, 0)
                mixer_output_node = add_single_node(mixer_group_tree, 'NodeGroupOutput', 900, 0)

                tint_multiply_node = add_single_node(mixer_group_tree, 'ShaderNodeVectorMath', 300, 0)
                exposure_exponent_node = add_single_node(mixer_group_tree, 'ShaderNodeMath', 300, -200)
                tint_exposure_multiply_node = add_single_node(mixer_group_tree, 'ShaderNodeVectorMath', 600, 0)

                tint_multiply_node.operation = "MULTIPLY"
                exposure_exponent_node.operation = 'EXPONENT'
                tint_exposure_multiply_node.operation = "MULTIPLY"

                # Пробрасываем линки
                mixer_group_tree.links.new(mixer_input_node.outputs['ALBEDO_RGB'], tint_multiply_node.inputs[0])
                mixer_group_tree.links.new(mixer_input_node.outputs['TINT'], tint_multiply_node.inputs[1])
                mixer_group_tree.links.new(mixer_input_node.outputs['EXPOSURE'], exposure_exponent_node.inputs[0])
                mixer_group_tree.links.new(tint_multiply_node.outputs[0], tint_exposure_multiply_node.inputs[0])
                mixer_group_tree.links.new(exposure_exponent_node.outputs[0], tint_exposure_multiply_node.inputs[1])
                mixer_group_tree.links.new(tint_exposure_multiply_node.outputs[0], mixer_output_node.inputs['ALBEDO_RGB'])
                
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