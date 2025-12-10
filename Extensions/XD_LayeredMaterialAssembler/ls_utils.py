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


def build_mat_graph():
    active_material = get_active_material()
    if active_material:
        nodes_count = len(active_material.node_tree.nodes.items())
        if nodes_count == 0:
            if active_material.node_tree:
                # Создаем входной узел
                input_node = active_material.node_tree.nodes.new('NodeGroupInput')
                input_node.location = (-300, 0)

                # Создаем выходной узел