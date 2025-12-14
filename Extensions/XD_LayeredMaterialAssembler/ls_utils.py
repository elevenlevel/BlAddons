import bpy
import json

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

def get_active_node_tree():
    space = bpy.context.space_data
    # Проверяем, что мы в Node Editor
    if space.type != 'NODE_EDITOR':
        return None
    # Получаем активный node_tree
    tree = space.node_tree
    if tree is None:
        # Если редактор открыт, но дерево не выбрано (редкий случай)
        return None
    return tree

def get_node_editor():
    space = bpy.context.space_data
    # Проверяем, что мы в Node Editor
    if space.type != 'NODE_EDITOR':
        return None
    return space

def remove_group_node(target_tree):
        selected_node = target_tree.nodes.active
        target_tree.nodes.remove(selected_node)

def create_group_node(target_tree, group_name="XXX"):
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

        # Связываем ноды внутри группы
        group_tree.links.new(groupinput.outputs['Base Color'], principled.inputs['Base Color'])
        group_tree.links.new(principled.outputs['BSDF'], groupoutput.inputs['BSDF'])

        # Добавляем ноду‑группу в целевой tree (куда нас попросили)
        group_node = target_tree.nodes.new('ShaderNodeGroup')
        group_node.name = group_name
        group_node.label = "XXX" + group_name
        group_node.node_tree = group_tree  # Привязываем созданное дерево группы
        group_node.location = (100, 100)  # Позиция в целевом дереве
        
        return group_tree

def build_mat_graph(group_name="XXX"):
    active_material = get_active_material()
    space = get_node_editor()
    
    if active_material is not None:
        
        tree = space.edit_tree
        if tree.type != "SHADER":
            print("tree.type: ", tree.type)
            return None
        
        print("tree.name: ", tree.name)
        if tree.name == "Shader Nodetree":
            target_tree = active_material.node_tree
        else:
            target_tree = tree
        
        selected_node = target_tree.nodes.active

        if selected_node and selected_node.type == "GROUP" and selected_node.label == "XXXXXX":
            bpy.ops.object.ask_to_replace_node('INVOKE_DEFAULT').target_tree = target_tree
        else:
            create_group_node(target_tree, group_name="XXX")