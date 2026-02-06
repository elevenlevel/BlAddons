import bpy
import json
from mathutils import Vector
import os

def get_matlayers_path(lm_path):
    """
    Docstring for get_matlayers_path
    """
    if lm_path == "":
        return None
    
    if not lm_path.endswith("~"):
        lm_path = lm_path + "~"
    
    return lm_path

def get_file_name(lm_path):
    """
    Docstring for get_matlayers_data
    """

    mat_layers_file = get_matlayers_path(lm_path)
    return os.path.splitext(os.path.basename(mat_layers_file))[0]

def get_matlayers_data(lm_path):
    """
    Docstring for get_matlayers_data
    """
    mat_layers_file = get_matlayers_path(lm_path)
    
    # читаем содержиме файла *.MatLayers
    try:
        with open(mat_layers_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except:
        return None

def get_active_material():
    """
    Docstring for get_active_material
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

def create_material():
    """
    Docstring for create_material
    """
    active_obj = bpy.context.active_object
    if not active_obj or active_obj.type != 'MESH':
        return None
    else:
        mat = bpy.data.materials.new(name="LayerMaterial")
        active_obj.data.materials.append(mat)
        return mat

def clean_mat_graph():
    """
    Docstring for clean_mat_graph
    """
    active_material = get_active_material()
    if active_material:
        if active_material.node_tree:
            active_material.node_tree.nodes.clear()
            active_material.node_tree.links.clear()

def get_active_tree():
    """
    Docstring for get_active_tree
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
    Docstring for get_active_node
    
    :param target_tree: Description
    """
    selected_nodes = [node for node in target_tree.nodes if node.select]

    if len(selected_nodes) != 0:
        result = target_tree.nodes.active
    else:
        result = None
    return result

def get_node_editor():
    """
    Docstring for get_node_editor
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
    Ищет свободное место на сетке.
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
        
        # Сдвигаемся по диагонали
        x += grid_size
        y -= grid_size


def remove_group_node(active_tree,
                    active_node):
        """
        Docstring for remove_group_node
        
        :param active_tree: Description
        :param active_node: Description
        """

        node_tree = active_node.node_tree
        active_tree.nodes.remove(active_node)

        if node_tree:
            print(f'remove node_tree: {node_tree.name}')
            bpy.data.node_groups.remove(node_tree)


def add_single_node(tree,
                    node_type: str='ShaderNodeTexImage',
                    loc_x: float=0.0,
                    loc_y: float=0.0):
        """
        Docstring for add_single_node
        """
        new_node = tree.nodes.new(node_type)
        new_node.location = (loc_x, loc_y)

        return new_node

def set_socket_value(node,
                    socket_name: str,
                    value):
                for input_socket in node.inputs:
                    if input_socket.name == socket_name:
                        input_socket.default_value = value  # Красный
                        break

def get_img_file(layer):
    if os.path.exists(layer):
        img = bpy.data.images.load(layer, check_existing=True)
        return img, None
    else:
        return None, "NO_TEXTURE"  # Флаг ошибки
        # addon_path = os.path.dirname(os.path.abspath(__file__))
        # no_tex_file = os.path.join(addon_path, 'NoTex.png')

        # if no_tex_file in bpy.data.images:
        #     img = bpy.data.images['no_tex_file']
        # else:
        #     img = bpy.data.images.load(no_tex_file, check_existing=True)
        


def check_existing_textures(lm_path):
    matlayers_data = get_matlayers_data(lm_path)
    matlayers_layers = matlayers_data['layers']
    file_path = get_matlayers_path(lm_path)

    bad_textures = bpy.context.scene.bad_textures
    for layer in matlayers_layers:
        for key, value in layer.items():
            if key == "albedo" or key == "geometry":
                abs_path = os.path.abspath(os.path.join(file_path, value))
                if not os.path.exists(abs_path):
                    new_bad_texture = bad_textures.add()
                    new_bad_texture.texture = abs_path
    
    if len(bpy.context.scene.bad_textures) > 0:
        bpy.ops.object.show_no_texture_dialog('INVOKE_DEFAULT')
        return False
    else:
        return True

def remove_ghosted_groups():
    print('Remove Ghosted Groups')
    
    def find_half_deleted_groups():
        """Находит группы, удаленные через DEL но оставшиеся в файле"""
        
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
        
        return ghosts
    
    ghost_groups = find_half_deleted_groups()
    
    for g in ghost_groups:
        try:
            bpy.data.node_groups.remove(g)
        except:
            print(f"Не удалось удалить: {g.name}")

def construct_group_node(active_tree: bpy.types.ShaderNodeTree,
                        matlayers_data: dict,
                        group_parms: str,
                        lm_path: str) -> None:
        """
        Docstring for create_group_node
        
        :param active_tree: Description
        :param group_name: Description
        """
        
        if not active_tree:
            print("Ошибка: active_tree не указан")
            return None
    
    ###===БЛОК ПОДГОТОВКИ ДАННЫХ===
        file_name = get_file_name(lm_path)

        if group_parms == None:
            group_name = f"{file_name} MAT LAYERS"
        else:
            group_name = group_parms['name']
        
        current_path = get_matlayers_path(lm_path)
        matlayers_layers = matlayers_data['layers']


    ###===БЛОК СОЗДАНИЯ ОСНОВНОЙ ГРУППЫ===###
        # Создаём новое дерево нод (NodeTree) для основной группы
        main_group_tree = bpy.data.node_groups.new(type='ShaderNodeTree', name=group_name)
        
        # Добавляем ноду‑группу в целевой tree
        main_group_node = add_single_node(active_tree, 'ShaderNodeGroup', 0, 0)

        layers = main_group_node.shader_links.layers

        # if main_group_node.shader_links.path != "":
        #     current_path = main_group_node.shader_links.path
        # else:
        #     current_path = bpy.context.window_manager.temp_path
        #main_group_node.shader_links.path = current_path
        
        
        for layer in matlayers_layers:
            albedo_rel = layer['albedo']
            
            albedo_abs = os.path.abspath(os.path.join(current_path, albedo_rel))
            geometry_rel = layer['geometry']
            geometry_abs = os.path.abspath(os.path.join(current_path, geometry_rel))

            new_layer = layers.add()


            new_layer.albedo = albedo_abs
            new_layer.geometry = geometry_abs
            new_layer.tint = layer['tint']['r'], layer['tint']['g'], layer['tint']['b'], layer['tint']['a']
            new_layer.exposure = layer['exposure']
            new_layer.smoothnessMultiplier = layer['smoothnessMultiplier']
            new_layer.metallic = layer['metallic']
        
        if group_parms == None:
            #  Позиция новой ноды
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
        # main_group_input_geometry_socket = main_group_tree.interface.new_socket(name='Geometry Map', in_out='INPUT', socket_type='NodeSocketColor') # NodeSocketFloat NodeSocketInt NodeSocketBool NodeSocketVector NodeSocketColor NodeSocketMenu NodeSocketShader NodeSocketBundle NodeSocketClosure
        main_group_input_menu_socket = main_group_tree.interface.new_socket(name='Layer', in_out='INPUT', socket_type='NodeSocketMenu')
        main_group_input_uv_socket = main_group_tree.interface.new_socket(name='uv', in_out='INPUT', socket_type='NodeSocketVector')
        main_group_input_uv_socket.hide_value = True
        
        main_group_output_albedo_socket = main_group_tree.interface.new_socket(name='Albedo', in_out='OUTPUT', socket_type='NodeSocketColor')
        main_group_output_normal_socket = main_group_tree.interface.new_socket(name='Normal', in_out='OUTPUT', socket_type='NodeSocketVector')
        main_group_output_height_socket = main_group_tree.interface.new_socket(name='Height', in_out='OUTPUT', socket_type='NodeSocketFloat')
        main_group_output_smoothness_socket = main_group_tree.interface.new_socket(name='Smoothness', in_out='OUTPUT', socket_type='NodeSocketFloat')
        main_group_output_metallic_socket = main_group_tree.interface.new_socket(name='Metallic', in_out='OUTPUT', socket_type='NodeSocketFloat')

        if group_parms != None:
            # восстанавливаем входные связи
            for node_socket, other_socket in group_parms["input_links"].items():
                node_socket = main_group_node.inputs[node_socket]
                active_tree.links.new(other_socket, node_socket)
            
            # восстанавливаем выходные связи
            for node_socket, other_socket in group_parms["output_links"].items():
                node_socket = main_group_node.outputs[node_socket]
                active_tree.links.new(other_socket, node_socket)
        
        main_group_node.shader_links.path = lm_path
        bpy.context.window_manager.temp_path = ""



    ###===БЛОК СОЗДАНИЯ ГРУПП СО СЛОЯМИ===###
        def create_map_group(node_parms: dict,
                            base_group_tree: bpy.types.ShaderNodeTree,
                            layer_name: str,
                            output_type: str) -> bpy.types.NodeGroup:
            
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
                    # Создаем выходы групп
                    numered_layer_name = layer_name+str(i)
                    group_output_socket = group_tree.interface.new_socket(name=f'Layer{i}', in_out='OUTPUT', socket_type=output_type)

                    albedo_layer_node = add_single_node(group_tree, 'ShaderNodeTexImage', 300, 300 * -i)

                    image, error = get_img_file(layer.albedo)
                    
                    albedo_layer_node.image = image

                    group_tree.links.new(albedo_group_input.outputs['uv'], albedo_layer_node.inputs['Vector'])

                    group_tree.links.new(albedo_layer_node.outputs['Color'], group_tree.nodes['Group Output'].inputs['Layer'+str(i)])
            
            ### NORMAL
            elif layer_name == 'Normal':
                for i, layer in enumerate(layers):
                    # Создаем выходы групп
                    numered_layer_name = layer_name+str(i)
                    group_output_socket = group_tree.interface.new_socket(name=f'Layer{i}', in_out='OUTPUT', socket_type=output_type)

                    image_layer_node = add_single_node(group_tree, 'ShaderNodeTexImage', 300, 300 * -i)
                    
                    image, error = get_img_file(layer.geometry)
                    
                    image_layer_node.image = image
                    image_layer_node.image.colorspace_settings.name = 'Non-Color'

                    separate_xyz_node = add_single_node(group_tree, 'ShaderNodeSeparateXYZ', 600, image_layer_node.location[1])
                    combine_xyz_node_0 = add_single_node(group_tree, 'ShaderNodeCombineXYZ', 900, image_layer_node.location[1]+50)
                    dot_prod_node = add_single_node(group_tree, 'ShaderNodeVectorMath', 1200, image_layer_node.location[1]+70)
                    dot_prod_node.operation = 'DOT_PRODUCT'
                    clamp_node = add_single_node(group_tree, 'ShaderNodeClamp', 1500, image_layer_node.location[1]+70)
                    clamp_node.clamp_type = 'MINMAX'
                    subtract_node = add_single_node(group_tree, 'ShaderNodeMath', 1800, image_layer_node.location[1]+70)
                    subtract_node.operation = 'SUBTRACT'
                    subtract_node.inputs[0].default_value = 1.0
                    square_root_node = add_single_node(group_tree, 'ShaderNodeMath', 2100, image_layer_node.location[1]+70)
                    square_root_node.operation = 'SQRT'
                    combide_xyz_node_1 = add_single_node(group_tree, 'ShaderNodeCombineXYZ', 2400, image_layer_node.location[1])
                    normalize_node = add_single_node(group_tree, 'ShaderNodeVectorMath', 2700, image_layer_node.location[1])
                    normalize_node.operation = 'NORMALIZE'


                    group_tree.links.new(albedo_group_input.outputs['uv'], image_layer_node.inputs['Vector'])
                    group_tree.links.new(image_layer_node.outputs['Color'], separate_xyz_node.inputs['Vector'])
                    group_tree.links.new(separate_xyz_node.outputs['X'], combine_xyz_node_0.inputs['X'])
                    group_tree.links.new(separate_xyz_node.outputs['Y'], combine_xyz_node_0.inputs['Y'])
                    group_tree.links.new(combine_xyz_node_0.outputs['Vector'], dot_prod_node.inputs[0])
                    group_tree.links.new(combine_xyz_node_0.outputs['Vector'], dot_prod_node.inputs[1])
                    group_tree.links.new(dot_prod_node.outputs['Value'], clamp_node.inputs['Value'])
                    group_tree.links.new(clamp_node.outputs['Result'], subtract_node.inputs[1])
                    group_tree.links.new(subtract_node.outputs[0], square_root_node.inputs[0])
                    group_tree.links.new(square_root_node.outputs['Value'], combide_xyz_node_1.inputs['Z'])
                    group_tree.links.new(separate_xyz_node.outputs['X'], combide_xyz_node_1.inputs['X'])
                    group_tree.links.new(separate_xyz_node.outputs['Y'], combide_xyz_node_1.inputs['Y'])
                    group_tree.links.new(combide_xyz_node_1.outputs['Vector'], normalize_node.inputs['Vector'])

                    group_tree.links.new(normalize_node.outputs['Vector'], group_tree.nodes['Group Output'].inputs['Layer'+str(i)])

                    group_tree.nodes['Group Output'].location.x = 3000
                
            ### HEIGHT
            elif layer_name == 'Height':
                for i, layer in enumerate(layers):
                    # Создаем выходы групп
                    numered_layer_name = layer_name+str(i)
                    group_output_socket = group_tree.interface.new_socket(name=f'Layer{i}', in_out='OUTPUT', socket_type=output_type)

                    image_layer_node = add_single_node(group_tree, 'ShaderNodeTexImage', 300, 300 * -i)
                    
                    image, error = get_img_file(layer.geometry)

                    # if error == "NO_TEXTURE":
                    #     bpy.ops.object.show_no_texture_dialog('INVOKE_DEFAULT')
                    #     return {'CANCELLED'}
                    
                    image_layer_node.image = image
                    image_layer_node.image.colorspace_settings.name = 'Non-Color'

                    separate_xyz_node = add_single_node(group_tree, 'ShaderNodeSeparateXYZ', 600, image_layer_node.location[1])

                    group_tree.links.new(albedo_group_input.outputs['uv'], image_layer_node.inputs['Vector'])

                    group_tree.links.new(image_layer_node.outputs['Color'], separate_xyz_node.inputs['Vector'])
                    group_tree.links.new(separate_xyz_node.outputs['Z'], group_tree.nodes['Group Output'].inputs['Layer'+str(i)])
            
            ### TINT
            elif layer_name == 'Tint':
                for i, layer in enumerate(layers):
                    # Создаем выходы групп
                    numered_layer_name = layer_name+str(i)
                    group_output_socket = group_tree.interface.new_socket(name=f'Layer{i}', in_out='OUTPUT', socket_type=output_type)

                    tint_layer_node = add_single_node(group_tree, 'ShaderNodeRGB', 300, 300 * -i)

                    tint_layer_node.outputs[0].default_value = layer.tint

                    group_tree.links.new(tint_layer_node.outputs['Color'], group_tree.nodes['Group Output'].inputs['Layer'+str(i)])
            
            ### EXPOSURE
            elif layer_name == 'Exposure':
                for i, layer in enumerate(layers):
                    # Создаем выходы групп
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
                    # Создаем выходы групп
                    numered_layer_name = layer_name+str(i)
                    group_output_socket = group_tree.interface.new_socket(name=f'Layer{i}', in_out='OUTPUT', socket_type=output_type)

                    smoothness_layer_node = add_single_node(group_tree, 'ShaderNodeValue', 300, 300 * -i)

                    smoothness_layer_node.outputs[0].default_value = layer.smoothnessMultiplier

                    group_tree.links.new(smoothness_layer_node.outputs['Value'], group_tree.nodes['Group Output'].inputs['Layer'+str(i)])
            
            ### METALLIC
            elif layer_name == 'Metallic':
                for i, layer in enumerate(layers):
                    # Создаем выходы групп
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
                                group_name: str="SWITCHER",):
            """
            Docstring for create_group_node
            
            :param active_tree: Description
            :param group_name: Description
            """
            
            if not active_tree:
                print("Ошибка: active_tree не указан")
                return None
            
            main_group_tree = bpy.data.node_groups.new(type='ShaderNodeTree', name=group_name)
            
            # Добавляем ноду‑группу в целевой tree
            switcher_node = add_single_node(active_tree, 'ShaderNodeGroup', 0, 0)
            
            switcher_node.name = group_name
            switcher_node.label = group_name + '_albedo'
            switcher_node.use_custom_color = True
            switcher_node.color = (0.28, 0.2, 0.3)
            switcher_node.location = master_node.location + Vector((300.0, 0.0))
            switcher_node.width = 140
            switcher_node.node_tree = main_group_tree  # Привязываем созданное дерево группы

            # Добавляем входные/выходные ноды albedo группы
            switcher_group_input = add_single_node(main_group_tree, 'NodeGroupInput', 0, 0)
            switcher_group_output = add_single_node(main_group_tree, 'NodeGroupOutput', 1000, 0)

            switcher_group_input_menu_socket = main_group_tree.interface.new_socket(name='Layer', in_out='INPUT', socket_type='NodeSocketMenu')

            # Создаем выходы групп
            switcher_group_output_socket = main_group_tree.interface.new_socket(name='result', in_out='OUTPUT', socket_type='NodeSocketColor')

            # соединяем сокеты меню
            input_node = active_tree.nodes.get('Group Input')
            menu_input = input_node.outputs['Layer']
            active_tree.links.new(menu_input, switcher_node.inputs['Layer'])

            for i, layer in enumerate(master_node.outputs):
                switcher_group_input_layer_socket = main_group_tree.interface.new_socket(name=f'Layer{i}', in_out='INPUT', socket_type='NodeSocketColor')
                
                set_socket_value(switcher_node, layer.name, (1.0, 0.0, 0.0, 1.0))

                # подключаем вход ноды
                active_tree.links.new(master_node.outputs[master_node.outputs[i].name], switcher_node.inputs[i+1])
            
            ### ===БЛОК ДОБАВЛЕНИЯ Menu Switch ВНУТРЬ СВИТЧЕРА===###
            switcher_node_tree = switcher_node.node_tree
            menu_switch_node = add_single_node(switcher_node_tree, 'GeometryNodeMenuSwitch', 300, 0)

            # удаляем дефолтные инпуты
            # menu_switch_node.enum_items[0].name = "Cylinder"
            # menu_switch_node.enum_items.new("MyNewItem")
            menu_switch_node.enum_items.remove(menu_switch_node.enum_items[1])
            menu_switch_node.enum_items.remove(menu_switch_node.enum_items[0])

            # добавляем новые инпуты
            # print(f"len of switcher_group_input.outputs = {len(switcher_group_input.outputs)}")
            for output in switcher_group_input.outputs:
                if output.name == 'Layer' or output.name == '':
                    continue
                menu_switch_node.enum_items.new(output.name)
                switcher_node_tree.links.new(switcher_node_tree.nodes['Group Input'].outputs[output.name], menu_switch_node.inputs[output.name])

            switcher_node_tree.links.new(switcher_node_tree.nodes['Group Input'].outputs['Layer'], menu_switch_node.inputs['Menu'])
            switcher_node_tree.links.new(menu_switch_node.outputs['Output'], switcher_node_tree.nodes['Group Output'].inputs['result'])

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
                
                main_group_tree.links.new(main_group_tree.nodes['Group Input'].outputs['Layer'], switcher_group_copy.inputs[0])
                
                
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

        # if main_group_node:
        #     matlayers_data = get_matlayers_data()['layers']
            
        # задаем дефолтное значение для меню
        if len(matlayers_data) > 0:
            main_group_node.inputs['Layer'].default_value = 'Layer0'

        # делаем ноду активной
        active_tree.nodes.active = main_group_node
        # bpy.context.view_layer.objects.active.select_set(True)

def def_mat_layers_node() -> bool:
    # определяем есть ли активная нода и mat_layers ли она
    active_node = get_active_node(get_active_tree())
    is_mat_layers_node = False

    if active_node:
        if active_node.type == "GROUP":
            if "mat_layers_data" in active_node:
                is_mat_layers_node = True
    
    return is_mat_layers_node

def add_node(group_name="Mat Layers", node_parms=None, lm_path=""):
    """
    Docstring for add_node
    
    :param group_name: Description
    """
    active_tree = get_active_tree()
    is_mat_layers_node = def_mat_layers_node()
    
    # если активная нода - это mat_layers, заменяем ее
    if is_mat_layers_node:
        print(f"Update selected Node")
        active_node = get_active_node(active_tree)
        lm_path = active_node.shader_links.path
        # bpy.ops.object.ask_to_replace_node('INVOKE_DEFAULT', lm_path=lm_path) # спрашиваем, заменить ли ноду и заменяем
    else: # если это НЕ mat_layers, создаем ноду с нуля
        print(f"Create new Mat Layers Node")

        matlayers_data = get_matlayers_data(lm_path)
        matlayers_layers = matlayers_data['layers']
        file_path = get_matlayers_path(lm_path)
        
        construct_group_node(active_tree, matlayers_data, None, lm_path=lm_path)
    node_c_props = None