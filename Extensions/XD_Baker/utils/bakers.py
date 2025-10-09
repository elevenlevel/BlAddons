import bpy
from .filters import set_rgb_from_alpha
from .functions import *


def bake_diffuse_map(context, map_name):
    cage_object = context.scene.xd_baker.temp_things.bake_cg_obj
    
    if get_options_var(context, map_name, "Albedo"): 
        p_filter = set({'COLOR'})
    else:
        p_filter = set({'DIRECT', 'INDIRECT', 'COLOR'})
    
    bpy.ops.object.bake(type="DIFFUSE", use_selected_to_active=True, use_cage=True, cage_object=cage_object.name, margin=0, pass_filter=p_filter)

def bake_ao_map(context, map_name):
    cage_object = context.scene.xd_baker.temp_things.bake_cg_obj
    
    nodes, override_mat = prepare_temp_material()
    material_output_node = nodes.get('Material Output')
    
    # добавляем ao шейдер и настраиваем его параметры
    ao_node = nodes.new('ShaderNodeAmbientOcclusion')
    ao_node.samples = get_options_var(context, map_name, "Samples")
    ao_node.inside = get_options_var(context, map_name, "Inside")
    ao_node.only_local = get_options_var(context, map_name, "Only Local")
    ao_node.inputs[1].default_value = get_options_var(context, map_name, "Distance")
    
    diffuse_node = nodes.new('ShaderNodeBsdfDiffuse')
    
    links = override_mat.node_tree.links
    links.new(ao_node.outputs[0], diffuse_node.inputs[0])
    links.new(diffuse_node.outputs[0], material_output_node.inputs[0])
    
    bake_temp_material(override_mat, cage_object.name)

def bake_normal_map(context, map_name):
    cage_object = context.scene.xd_baker.temp_things.bake_cg_obj
    
    y = "POS_Y"
    if get_options_var(context, map_name, "Invert Green"):
        y = "NEG_Y"
    bpy.ops.object.bake(type="NORMAL", use_selected_to_active=True, use_cage=True, cage_object=cage_object.name, margin=0, normal_r="POS_X", normal_g=y, normal_b="POS_Z")

def bake_normal_os_map(context, map_name):
    cage_object = context.scene.xd_baker.temp_things.bake_cg_obj
    
    nodes, override_mat = prepare_temp_material()
    material_output_node = nodes.get('Material Output')
    
    # создаем нодовую структуру для normal os в цвете
    geometry_node = nodes.new('ShaderNodeNewGeometry')
    normalize_node = nodes.new('ShaderNodeVectorMath')
    normalize_node.operation = 'NORMALIZE'
    mul_add_node = nodes.new('ShaderNodeVectorMath')
    mul_add_node.operation = 'MULTIPLY_ADD'
    mul_add_node.inputs[1].default_value = [0.5, 0.5, 0.5]
    mul_add_node.inputs[2].default_value = [0.5, 0.5, 0.5]
    diffuse_node = nodes.new('ShaderNodeBsdfDiffuse')
    
    links = override_mat.node_tree.links
    links.new(diffuse_node.outputs[0], material_output_node.inputs[0])
    links.new(mul_add_node.outputs[0], diffuse_node.inputs[0])
    links.new(normalize_node.outputs[0], mul_add_node.inputs[0])
    links.new(geometry_node.outputs[1], normalize_node.inputs[0])
    
    bake_temp_material(override_mat, cage_object.name)

def bake_position_map(context, map_name):
    cage_object = context.scene.xd_baker.temp_things.bake_cg_obj
    
    nodes, override_mat = prepare_temp_material()
    material_output_node = nodes.get('Material Output')
    
    # создаем нодовую структуру для позиции в цвете
    geometry_node = nodes.new('ShaderNodeNewGeometry')
    normalize_node = nodes.new('ShaderNodeVectorMath')
    normalize_node.operation = 'NORMALIZE'
    mul_add_node = nodes.new('ShaderNodeVectorMath')
    mul_add_node.operation = 'MULTIPLY_ADD'
    mul_add_node.inputs[1].default_value = [0.5, 0.5, 0.5]
    mul_add_node.inputs[2].default_value = [0.5, 0.5, 0.5]
    diffuse_node = nodes.new('ShaderNodeBsdfDiffuse')
    
    links = override_mat.node_tree.links
    links.new(diffuse_node.outputs[0], material_output_node.inputs[0])
    links.new(mul_add_node.outputs[0], diffuse_node.inputs[0])
    links.new(normalize_node.outputs[0], mul_add_node.inputs[0])
    links.new(geometry_node.outputs[0], normalize_node.inputs[0])
    
    bake_temp_material(override_mat, cage_object.name)

def bake_roughness_map(context, map_name):
    cage_object = context.scene.xd_baker.temp_things.bake_cg_obj
    
    bpy.ops.object.bake(type="ROUGHNESS", use_selected_to_active=True, use_cage=True, cage_object=cage_object.name, margin=0)

def bake_emission_map(context, map_name):
    cage_object = context.scene.xd_baker.temp_things.bake_cg_obj
    
    bpy.ops.object.bake(type="EMIT", use_selected_to_active=True, use_cage=True, cage_object=cage_object.name, margin=0)

def bake_curvature_map(context, map_name):
    cage_object = context.scene.xd_baker.temp_things.bake_cg_obj
    
    nodes, override_mat = prepare_temp_material()
    material_output_node = nodes.get('Material Output')
    
    # создаем нодовую структуру для curvature в цвете
    geometry_node = nodes.new('ShaderNodeNewGeometry')
    diffuse_node = nodes.new('ShaderNodeBsdfDiffuse')
    
    links = override_mat.node_tree.links
    links.new(diffuse_node.outputs[0], material_output_node.inputs[0])
    links.new(geometry_node.outputs[7], diffuse_node.inputs[0])
    
    bake_temp_material(override_mat, cage_object.name)

def bake_edge_wear_map(context, map_name):
    cage_object = context.scene.xd_baker.temp_things.bake_cg_obj
    
    nodes, override_mat = prepare_temp_material()
    material_output_node = nodes.get('Material Output')
    
    # создаем нодовую структуру для edge wear в цвете
    diffuse_node = nodes.new('ShaderNodeBsdfDiffuse')
    geometry_node = nodes.new('ShaderNodeNewGeometry')
    bevel_node = nodes.new('ShaderNodeBevel')
    bevel_node.samples = get_options_var(context, map_name, "Samples")
    bevel_node.inputs[0].default_value = get_options_var(context, map_name, "Strength")
    dot_product_node = nodes.new('ShaderNodeVectorMath')
    dot_product_node.operation = 'DOT_PRODUCT'
    
    links = override_mat.node_tree.links
    links.new(diffuse_node.outputs[0], material_output_node.inputs[0])
    links.new(dot_product_node.outputs[1], diffuse_node.inputs[0])
    links.new(bevel_node.outputs[0], dot_product_node.inputs[0])
    links.new(geometry_node.outputs[1], dot_product_node.inputs[1])
    links.new(geometry_node.outputs[1], bevel_node.inputs[1])
    
    bake_temp_material(override_mat, cage_object.name)

def bake_vertex_color_map(context, map_name):
    cage_object = context.scene.xd_baker.temp_things.bake_cg_obj
    
    nodes, override_mat = prepare_temp_material()
    material_output_node = nodes.get('Material Output')
    
    # создаем нодовую структуру для vertex_color в цвете
    vertex_color_node = nodes.new('ShaderNodeVertexColor')
    vertex_color_node.layer_name = get_options_var(context, map_name, "Attribute")
    diffuse_node = nodes.new('ShaderNodeBsdfDiffuse')
    
    links = override_mat.node_tree.links
    links.new(diffuse_node.outputs[0], material_output_node.inputs[0])
    links.new(vertex_color_node.outputs[0], diffuse_node.inputs[0])
    
    bake_temp_material(override_mat, cage_object.name)

def bake_height_map(context, map_name):
    cage_object = context.scene.xd_baker.temp_things.bake_cg_obj
    
    # TODO: realize highmap bake
    #bpy.ops.object.bake(type="EMIT", use_selected_to_active=True, use_cage=True, cage_object=cage_object, margin=0)
    #report({'WARNING'}, "Height map temporary not supported")
    pass

def bake_opacity_map(context, map_name):
    cage_object = context.scene.xd_baker.temp_things.bake_cg_obj
    
    bpy.ops.object.bake(type="DIFFUSE", use_selected_to_active=True, use_cage=True, cage_object=cage_object.name, margin=0, pass_filter=set({'COLOR'}))
    sdf_expanded = get_options_var(context, map_name, "SDF Expanded")
    sdf_shrinked = get_options_var(context, map_name, "SDF Shrinked")
    
    if sdf_expanded and not sdf_shrinked: sdf_type = 'SDF Expanded'
    elif sdf_shrinked and not sdf_expanded: sdf_type = 'SDF Shrinked'
    elif sdf_expanded and sdf_shrinked: sdf_type = 'SDF Mixed'
    elif not sdf_expanded and not sdf_shrinked: sdf_type = 'None'
    
    set_rgb_from_alpha(context, sdf_type)

def bake_custom_map(context, map_name):
    cage_object = context.scene.xd_baker.temp_things.bake_cg_obj
    # TODO: realize custom map bake
    #bpy.ops.object.bake(type="EMIT", use_selected_to_active=True, use_cage=True, cage_object=cage_object, margin=0)
    #report({'WARNING'}, "Custom map temporary not supported")
    pass

def bake_uv_wire_map(context, map_name):
    baked_texture = context.scene.xd_baker.attributes.baked_texture
    baked_texture_name = baked_texture.name
    
    low_poly_obj = context.scene.xd_baker.attributes.low_poly_obj
    bake_lp_obj = context.scene.xd_baker.temp_things.bake_lp_obj
    
    img_bake_width = context.scene.xd_baker.attributes.img_bake_width
    img_bake_height = context.scene.xd_baker.attributes.img_bake_height
    if context.scene.xd_baker.attributes.link_width_height: img_bake_height = img_bake_width
    image_size = (img_bake_width, img_bake_height)
    
    # снимаем выделение со всех объектов и назначаем активным наш
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = bake_lp_obj
    
    # переходим в edit mode и выделяем все полигоны
    old_mode = bpy.context.object.mode
    if old_mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.mode_set(mode=old_mode)
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, prefix="XD_Baker__", suffix=".png")
    temp_file_path = temp_file.name
    
    uv_num = get_options_var(context, map_name, "UV Map")
    udim_enable = get_options_var(context, map_name, "UDIM")
    
    tiles = 'NONE'
    if udim_enable:
        #tiles = 'UDIM'  # udim_enable не учитывается
        pass
    
    uv_layers = bake_lp_obj.data.uv_layers
    
    for idx, layer in enumerate(uv_layers):
        if idx != uv_num:
            layer.active = False
        else:
            layer.active = True
    
    bpy.ops.uv.export_layout(filepath=temp_file_path, size=image_size, mode='PNG', modified=False, export_tiles=tiles) # бейк для embedded текстуры в проекте
    
    image_name = baked_texture_name
    
    if image_name in bpy.data.images:
        bpy.data.images.remove(bpy.data.images.get(image_name))
    
    image = load_image(temp_file_path)
    image.name = baked_texture_name
    context.scene.xd_baker.attributes.baked_texture = image
    
    if context.scene.xd_baker.attributes.enable_save:
        file_save_path = set_texture_addon_folder(context)
        if file_save_path.endswith('.tif'):
            file_save_path = file_save_path[:-4]
        bpy.ops.uv.export_layout(filepath=file_save_path, size=image_size, mode='EPS', modified=False, export_tiles=tiles) # бейк во внешний файл
