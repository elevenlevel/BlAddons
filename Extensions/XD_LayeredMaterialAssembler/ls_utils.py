import bpy
import json
from mathutils import Vector

def get_matlayers_path():
    return bpy.context.scene.shader_links.path

def get_matlayers_data():
    mat_layers_file = get_matlayers_path()
    # читаем содержиме файла *.MatLayers
    try:
        with open(mat_layers_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def get_active_material():
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
    active_obj = bpy.context.active_object
    if not active_obj or active_obj.type != 'MESH':
        return None
    else:
        mat = bpy.data.materials.new(name="LayerMaterial")
        active_obj.data.materials.append(mat)
        return mat

def clean_mat_graph():
    active_material = get_active_material()
    if active_material:
        if active_material.node_tree:
            active_material.node_tree.nodes.clear()
            active_material.node_tree.links.clear()

def get_active_tree():
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
    return target_tree.nodes.active

def get_node_editor():
    space = bpy.context.space_data
    # Проверяем, что мы в Node Editor
    if space.type != 'NODE_EDITOR':
        return None
    return space

def get_node_editor_center():
    """
    Возвращает центр видимой области Node Editor в координатах пространства нод.
    
    Returns:
        Vector(x, y) — центр в координатах нод, или None если Node Editor не найден
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
    
    return None

def get_screen_center():
    """
    Возвращает центр видимой области Node Editor в координатах нод.
    
    Returns:
        Vector(x, y) — центр видимой зоны, или None если Node Editor не найден
    """
    for area in bpy.context.screen.areas:
        if area.type == 'NODE_EDITOR':
            # Находим основную область (где отображаются ноды)
            region = next((r for r in area.regions if r.type == 'WINDOW'), None)
            if not region:
                continue
            
            
            # Получаем объект View2D
            view2d = region.view2d
            
            
            # Границы видимой области в координатах нод
            view_min = Vector(view2d.view_min)
            view_max = Vector(view2d.view_max)
            
            
            # Центр — среднее между min и max
            center = (view_min + view_max) / 2
            return center

    return None

def remove_group_node(active_tree, active_node):
        active_tree.nodes.remove(active_node)

def create_group_node(active_tree, group_name="XXX"):
        # Создаём новое дерево нод (NodeTree) для группы
        group_tree = bpy.data.node_groups.new(type='ShaderNodeTree', name='MyPrincipledGroup')
        
        # Добавляем Principled BSDF в дерево группы
        principled = group_tree.nodes.new('ShaderNodeBsdfPrincipled')
        principled.location = (0, 0)  # Позиция внутри группы

        # Добавляем входные/выходные ноды группы
        groupinput = group_tree.nodes.new('NodeGroupInput')
        groupinput.location = (-300, 0)

        groupoutput = group_tree.nodes.new('NodeGroupOutput')
        groupoutput.location = (300, 0)
        
        # Можно настроить параметры Principled (опционально)
        # principled.inputs['Base Color'].default_value = (1.0, 0.0, 0.0, 1.0)
        # principled.inputs['Metallic'].default_value = 0.5
        # principled.inputs['Roughness'].default_value = 0.3
        
        # Создаём сокеты через interface (новый API Blender 5.0+)
        # Вход для Base Color
        input_socket = group_tree.interface.new_socket(
            name='Base Color',
            in_out='INPUT',
            socket_type='NodeSocketColor'
        )
        
        # Выход для BSDF
        output_socket = group_tree.interface.new_socket(
            name='BSDF',
            in_out='OUTPUT',
            socket_type='NodeSocketShader'
        )
        
        center = get_node_editor_center()

        # Связываем ноды внутри группы
        group_tree.links.new(groupinput.outputs['Base Color'], principled.inputs['Base Color'])
        group_tree.links.new(principled.outputs['BSDF'], groupoutput.inputs['BSDF'])

        # Добавляем ноду‑группу в целевой tree (куда нас попросили)
        group_node = active_tree.nodes.new('ShaderNodeGroup')
        group_node.name = group_name
        group_node.label = group_name
        group_node.use_custom_color = True
        group_node.color = (1.0, 0.5, 0.0)
        # group_node.location = (100, 100)  # Позиция в целевом дереве
        group_node.location = get_node_editor_center()
        print("location: ", group_node.location)
        print("location_absolute: ", group_node.location_absolute)
        group_node.node_tree = group_tree  # Привязываем созданное дерево группы
        
        
        print(f"Центр видимой зоны: X={center.x:.2f}, Y={center.y:.2f}")
        return group_node

def refresh_group_node(active_tree, group_parms):
        group_name=group_parms["name"]
        group_label = group_parms["label"]
        group_use_custom_color = group_parms["use_custom_color"]
        group_color = group_parms["color"]
        group_custom = group_parms["custom_properties"]
        group_location = group_parms["location"]
        input_sockets = group_parms["input_sockets"]
        output_sockets = group_parms["output_sockets"]

        # Создаём новое дерево нод (NodeTree) для группы
        group_tree = bpy.data.node_groups.new(type='ShaderNodeTree', name=group_name)
        
        # Добавляем Principled BSDF в дерево группы
        principled = group_tree.nodes.new('ShaderNodeBsdfPrincipled')
        principled.location = (0, 0)  # Позиция внутри группы

        # Добавляем входные/выходные ноды группы
        groupinput = group_tree.nodes.new('NodeGroupInput')
        groupinput.location = (-300, 0)

        groupoutput = group_tree.nodes.new('NodeGroupOutput')
        groupoutput.location = (300, 0)
        
        # Можно настроить параметры Principled (опционально)
        # principled.inputs['Base Color'].default_value = (1.0, 0.0, 0.0, 1.0)
        # principled.inputs['Metallic'].default_value = 0.5
        # principled.inputs['Roughness'].default_value = 0.3
        
        # Создаём сокеты через interface (новый API Blender 5.0+)
        # Вход для Base Color
        input_socket = group_tree.interface.new_socket(
            name='Base Color',
            in_out='INPUT',
            socket_type='NodeSocketColor'
        )
        
        # Выход для BSDF
        output_socket = group_tree.interface.new_socket(
            name='BSDF',
            in_out='OUTPUT',
            socket_type='NodeSocketShader'
        )

        # Связываем ноды внутри группы
        group_tree.links.new(groupinput.outputs['Base Color'], principled.inputs['Base Color'])
        group_tree.links.new(principled.outputs['BSDF'], groupoutput.inputs['BSDF'])

        # Добавляем ноду‑группу в целевой tree (куда нас попросили)
        group_node = active_tree.nodes.new('ShaderNodeGroup')
        group_node.name = group_name
        group_node.label = group_label
        group_node.node_tree = group_tree  # Привязываем созданное дерево группы
        group_node.location = (100, 100)  # Позиция в целевом дереве

        return group_tree

def build_mat_graph(group_name="XXX"):
    active_tree = get_active_tree()
    active_node = get_active_node(active_tree)

    if active_node and active_node.type == "GROUP" and active_node.label == "XXX":
        bpy.ops.object.ask_to_replace_node('INVOKE_DEFAULT')
    else:
        create_group_node(active_tree, group_name)

