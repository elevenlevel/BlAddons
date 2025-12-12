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

def build_mat_graph():
    active_material = get_active_material()
    space = get_node_editor()
    
    if active_material is not None:
        
        tree = space.edit_tree
        if tree.type == "SHADER":
            return None
        
        if tree.name == "Shader Nodetree":
            node_tree = active_material.node_tree
        else:
            node_tree = tree.node_tree
        
        # Создаем входной узел
        input_node = node_tree.nodes.new('NodeGroupInput')
        input_node.location = (-300, 0)
        # Создаем выходной узел
        output_node = node_tree.nodes.new('NodeGroupOutput')
        output_node.location = (300, 0)
        bpy.data.node_groups['MatLayers'].append(input_node)
        bpy.data.node_groups['MatLayers'].append(output_node)
        # Создаем группу
        group = node_tree.nodes.new('ShaderNodeGroup')
        group.node_tree = bpy.data.node_groups['MatLayers']
        group.location = (0, 0)
        # Создаем связи
        # material.node_tree.links.new(input_node.outputs['Surface'], group.inputs['Surface'])
        