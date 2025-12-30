import bpy
import json
from mathutils import Vector

def get_matlayers_path():
    """
    Docstring for get_matlayers_path
    """
    if bpy.context.scene.shader_links.path.endswith("~"):
        result_path = bpy.context.scene.shader_links.path
    else:
        result_path = bpy.context.scene.shader_links.path + "~"
    print(f"resilt_path: {result_path}")
    return result_path

def get_matlayers_data():
    """
    Docstring for get_matlayers_data
    """
    mat_layers_file = get_matlayers_path()
    print(f'read mat_layers_file: {mat_layers_file}')
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
    return target_tree.nodes.active

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

def calc_new_node_pos(target_tree):
    center = get_node_editor_center()
    def get_overlapped(center):
        try:
            for node in target_tree.nodes:
                node_pos = node.location
                node_size = node.dimensions
                
                overlap_x = False
                overlap_y = False

                if node_pos.x > (center.x - node_size.x * 0.5) or node_pos.x < (center.x + node_size.x * 0.5):
                    overlap_x = True
                if node_pos.y > (center.y - node_size.y * 0.5) or node_pos.y < (center.y + node_size.y * 0.5):
                    overlap_y = True

                if overlap_x and overlap_y:
                    center = center + Vector((node_size.x*0.5, node_size.y*-0.5))
                    # get_overlapped(center)
                    return center
                
                return center
        except:
            return center
            
    return get_overlapped(center)

def remove_group_node(active_tree, active_node):
        """
        Docstring for remove_group_node
        
        :param active_tree: Description
        :param active_node: Description
        """
        active_tree.nodes.remove(active_node)

def add_single_node(tree, node_type='ShaderNodeTexImage', loc_x=0.0, loc_y=0.0):
        """
        Docstring for add_single_node
        """
        new_node = tree.nodes.new(node_type)
        new_node.location = (loc_x, loc_y)

        return new_node

def construct_group_node(active_tree, group_name="XXX"):
        """
        Docstring for create_group_node
        
        :param active_tree: Description
        :param group_name: Description
        """

        if not active_tree:
            print("Ошибка: active_tree не указан")
            return None




    ###===БЛОК СОЗДАНИЯ ОСНОВНОЙ ГРУППЫ===###
        # Создаём новое дерево нод (NodeTree) для основной группы
        main_group_tree = bpy.data.node_groups.new(type='ShaderNodeTree', name=group_name)
        
        # Добавляем ноду‑группу в целевой tree
        main_group_node = add_single_node(active_tree, 'ShaderNodeGroup', 0, 0)
        
        #  Позиция новой ноды
        new_node_loc = calc_new_node_pos(active_tree)
        
        main_group_node.name = group_name
        main_group_node.label = group_name
        main_group_node.use_custom_color = True
        main_group_node.color = (0.28, 0.2, 0.3)
        main_group_node.location = new_node_loc
        main_group_node.width = 240
        main_group_node.node_tree = main_group_tree  # Привязываем созданное дерево группы
        main_group_node['Mat Layers'] = {'name':'my group',  'label':'my label', 'size':100}
        
        # Добавляем входные/выходные ноды основной группы
        main_group_input = add_single_node(main_group_tree, 'NodeGroupInput', 0, 0)
        main_group_output = add_single_node(main_group_tree, 'NodeGroupOutput', 2000, 0)
        
        # Создаём входы и выходы основной группы
        # main_group_input_geometry_socket = main_group_tree.interface.new_socket(name='Geometry Map', in_out='INPUT', socket_type='NodeSocketColor') # NodeSocketFloat NodeSocketInt NodeSocketBool NodeSocketVector NodeSocketColor NodeSocketMenu NodeSocketShader NodeSocketBundle NodeSocketClosure
        main_group_input_uv_socket = main_group_tree.interface.new_socket(name='uv', in_out='INPUT', socket_type='NodeSocketVector')
        main_group_input_uv_socket.hide_value = True

        main_group_output_albedo_socket = main_group_tree.interface.new_socket(name='Albedo', in_out='OUTPUT', socket_type='NodeSocketColor')
        main_group_output_normal_socket = main_group_tree.interface.new_socket(name='Normal', in_out='OUTPUT', socket_type='NodeSocketVector')
        main_group_output_height_socket = main_group_tree.interface.new_socket(name='Height', in_out='OUTPUT', socket_type='NodeSocketFloat')
        main_group_output_smoothness_socket = main_group_tree.interface.new_socket(name='Smoothness', in_out='OUTPUT', socket_type='NodeSocketFloat')
        main_group_output_metallic_socket = main_group_tree.interface.new_socket(name='Metallic', in_out='OUTPUT', socket_type='NodeSocketFloat')





    ###===БЛОК СОЗДАНИЯ ГРУПП СО СЛОЯМИ===###
        def create_map_group(base_group_tree, layer_name, output_type):
            layer_name = layer_name.capitalize()
            layer_group_name = layer_name + 'LayersGroup'

            node_parms = {
                'Albedo': [(0.47, 0.5, 0.61), (900, 0)],
                'Normal': [(0.38, 0.37, 0.59), (900, -300)],
                'Height': [(0.38, 0.32, 0.29), (900, -600)],
                'Tint': [(0.42, 0.61, 0.43), (900, -900)],
                'Exposure': [(0.76, 0.77, 0.53), (900, -1200)],
                'Smoothness': [(0.61, 0.61, 0.61), (900, -1500)],
                'Metallic': [(0.42, 0.42, 0.42), (900, -1800)]
                }

            # Добавляем группу
            group_tree = bpy.data.node_groups.new(type='ShaderNodeTree', name=layer_group_name)
            
            # Добавляем ноду‑группу в целевой tree
            group_node = add_single_node(base_group_tree, 'ShaderNodeGroup', 0, 0)
            
            group_node.name = layer_group_name
            group_node.label = layer_group_name
            group_node.use_custom_color = True
            group_node.color = node_parms[layer_name][0]
            group_node.location = node_parms[layer_name][1]
            group_node.width = 240
            group_node.node_tree = group_tree  # Привязываем созданное дерево группы
            
            # Добавляем входные/выходные ноды albedo группы
            albedo_group_input = add_single_node(group_tree, 'NodeGroupInput', 0, 0)
            albedo_group_output = add_single_node(group_tree, 'NodeGroupOutput', 1000, 0)

            albedo_group_input_uv_socket = group_tree.interface.new_socket(name='uv', in_out='INPUT', socket_type='NodeSocketVector')

            # Создаем выходы групп
            albedo_group_output_socket = group_tree.interface.new_socket(name=layer_name, in_out='OUTPUT', socket_type=output_type)
            
            # подключаем вход ноды albedo group связями
            base_group_tree.links.new(main_group_input.outputs['uv'], group_node.inputs['uv'])

            layers = bpy.context.scene.shader_links.layers
            print(f"layers: {layers}")

        ###===БЛОК СОЗДАНИЯ СЛОЕВ===###
            if layer_name == 'Albedo':
                for i, layer in enumerate(layers):
                    albedo_layer_node = add_single_node(group_tree, 'ShaderNodeTexImage', 300, 300 * -i)

                    img = bpy.data.images.load("D:\\__Repositories\\BlAddons\\Misc\\SwampTerrain_id.png", check_existing=True)
                    albedo_layer_node.image = img

                    group_tree.links.new(albedo_group_input.outputs['uv'], albedo_layer_node.inputs['Vector'])
                
            # elif layer_name == 'normal':
            # elif layer_name == 'height':
            # elif layer_name == 'tint':
            # elif layer_name == 'exposure':
            # elif layer_name == 'smoothness':
            # elif layer_name == 'metallic':


        create_map_group(main_group_tree, 'albedo', 'NodeSocketColor')
        create_map_group(main_group_tree, 'normal', 'NodeSocketVector')
        create_map_group(main_group_tree, 'height', 'NodeSocketFloat')
        create_map_group(main_group_tree, 'tint', 'NodeSocketColor')
        create_map_group(main_group_tree, 'exposure', 'NodeSocketFloat')
        create_map_group(main_group_tree, 'smoothness', 'NodeSocketFloat')
        create_map_group(main_group_tree, 'metallic', 'NodeSocketFloat')





def refresh_group_node(active_tree, group_parms):
        """
        Docstring for refresh_group_node
        
        :param active_tree: Description
        :param group_parms: Description
        """

        return

def add_node(group_name="Mat Layers", node_parms=None):
    """
    Docstring for add_node
    
    :param group_name: Description
    """
    active_tree = get_active_tree()
    active_node = get_active_node(active_tree)
    
    # определяем есть ли активная нода и mat_layers ли она
    mat_layers_node = None
    if active_node:
        if active_node.type == "GROUP":
            if "mat_layers" in active_node.node_tree["CustomProperties"]:
                mat_layers_node = active_node


    # если активная нода - это mat_layers, заменяем ее
    if mat_layers_node:
        print(f"Обновляем текущую ноду")
        node_c_props = active_node.node_tree["CustomProperties"]
        mat_layers = node_c_props["mat_layers"]
        bpy.ops.object.ask_to_replace_node('INVOKE_DEFAULT') # спрашиваем, заменить ли ноду и заменяем
    else: # если это НЕ mat_layers, создаем ноду с нуля
        print(f"Обновляем текущую ноду")
        construct_group_node(active_tree, group_name)
    node_c_props = None
