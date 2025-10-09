# from . py_modules import cv2 as cv
import bpy, os, time, gpu, tempfile
from gpu_extras.batch import batch_for_shader
import numpy as np
import bmesh
from .filters import *
from .cage import *
from ..addon_data import object_render_status, object_selection_status, object_active_status, cage_colors

def start_timer():
    return time.time()

def end_timer(self, start_time):
    # считаем время выполнения
    end_time = time.time()
    time_taken = end_time - start_time
    minutes = int(time_taken // 60)
    seconds = int(time_taken % 60)
    time_str = "{}.m {}.s".format(minutes, seconds)
    message = "Total baking time: " + time_str
    self.report({'INFO'}, message)

def get_node(node_type, node_tree):
    for node in node_tree.nodes:
        if node.type == node_type:
            return node
    return None

def backup_objects_render_state(): # собираем данные о скрытии всех объектов в сцене
    for obj in bpy.data.objects:
        object_render_status[obj.name] = obj.hide_render

def restore_objects_render_state(): # восстанавливаем данные о скрытии всех объектов в сцене
    for obj in bpy.data.objects:
        if obj.name in object_render_status:
            obj.hide_render = object_render_status[obj.name]

def backup_objects_selection():
    for obj in bpy.data.objects:
        object_selection_status[obj.name] = obj.select_get()
        if obj == bpy.context.view_layer.objects.active:
            object_active_status[obj.name] = True

def restore_objects_selection():
    for obj_name in object_selection_status:
        bpy.data.objects[obj_name].select_set(object_selection_status[obj_name])
        if obj_name in object_active_status:
            bpy.context.view_layer.objects.active = bpy.data.objects[obj_name]

def create_object_copy(scene, object, clear_materials=False):
    obj_copy = object.copy()
    obj_copy.data = object.data.copy()
    obj_copy.animation_data_clear()
    obj_copy.name = object.name + "_copy"
    
    if clear_materials:
        obj_copy.data.materials.clear()
    
    scene.collection.objects.link(obj_copy)
    return obj_copy

def ignore_group(context, map_name, name_test='AO', scene_objects=None): # раскидываем объекты в пространстве чтобы запекались отдельно
    if map_name == name_test and get_options_var(context, map_name, "Ignore Group"):
        for i, obj_copy in enumerate(scene_objects):
            obj_copy.location[1] += i * 100.0

def is_collection(context): # проверяем, является ли выбранный объект коллекцией
    selected_objects = context.selected_objects

    try:
        mesh_object = selected_objects[0].users_collection
    except:
        mesh_object = None
                
    if mesh_object == None:
        return True
    else:
        return False
                
def add_link_by_index(self, node_tree, node, node2, output_name, input_index):
    node_tree.links.new(node.outputs[output_name], node2.inputs[input_index])

def add_link(self, node_tree, node, node2, output_name, input_name, non_color_data = False):
    node_tree.links.new(node.outputs[output_name], node2.inputs[input_name])

def get_excluded_collections(collection, all_collections): # определяем включенные/выключенные коллекции
    col_type = type(collection).__name__
    col_children = collection.children
    if col_type != 'bpy_prop_collection' and col_type != 'LayerCollection':
        return
    
    col_children = collection.children
    for child in col_children:
        try:
            current = all_collections[child.name]
            # внедряем метку включения/выключения коллекции
            current['excluded'] = child.exclude
        except:
            pass
        # рекурсия
        get_excluded_collections(child, all_collections)

def combine_couples(context, map_name = ""):
    scene = context.scene

    high_poly = context.scene.xd_baker.attributes.high_poly_obj
    low_poly = context.scene.xd_baker.attributes.low_poly_obj
    low_poly_old_name = low_poly.name

    high_poly = create_object_copy(scene, high_poly, clear_materials=False)
    low_poly = create_object_copy(scene, low_poly, clear_materials=True)
    context.scene.xd_baker.attributes.bake_texture_name = low_poly_old_name

    return high_poly, low_poly


def combine_collections(context, collection=None, map_name=""):
    """Берем low и high poly объекты и делаем их копии и объединяем
    Тем самым получаем отдельные объекты для запекания. Благодаря этому можем печь множество объектов сразу
    и вносить изменения в эти объекты на разных уровнях."""

    scene = context.scene

    high_poly = None
    low_poly = None

    scene_collections = bpy.data.collections
    single_collection = scene_collections[collection.name]
    collection_objects = None
    
    collection_objects = single_collection.all_objects # все объекты текущей коллекции

    # разбираем объекты коллекции на high и low
    high_array = [obj for obj in collection_objects if obj.type == 'MESH' and obj.name.lower().endswith("_high")]
    low_array = [obj for obj in collection_objects if obj.type == 'MESH' and obj.name.lower().endswith("_low")]
    
    if len(high_array) == 0 and len(low_array) == 0:
        print("No matching objects in the collection" + single_collection.name)
        return None, None

    elif len(high_array) == 0:
        print("No '_high' Poly Objects in the Collection" + single_collection.name)
        return None, None
    
    elif len(low_array) == 0:
        print("No '_low' Poly Objects in the Collection" + single_collection.name)
        return None, None
    
    elif len(high_array) != len(low_array):
        print("'_high' and '_low' counts issue in the collection" + single_collection.name)
        return None, None
    
    # сортируем содержимое массивов high_array и low_array по имени объекта
    high_array.sort(key = lambda o: o.name)
    low_array.sort(key = lambda o: o.name)



    # \\_РАБОТАЕМ С ОБЪЕКТАМИ HIGH POLY_//
    for obj in high_array: # выделяем объекты
        obj.select_set(True)

    if len(high_array) == 1:
        obj = high_array[0]
        high_poly = create_object_copy(scene, obj, clear_materials=False)
    elif len(high_array) > 1:
        copied_objects = []
        for obj in high_array:
            obj_copy = create_object_copy(scene, obj, clear_materials=False)
            copied_objects.append(obj_copy)
        
        ignore_group(context, map_name, 'AO', copied_objects)
        bpy.ops.object.select_all(action='DESELECT')

        for obj in copied_objects:
            obj.select_set(True)
        
        bpy.context.view_layer.objects.active = copied_objects[0]
        bpy.ops.object.join()
        high_poly = bpy.context.active_object



    # \\_РАБОТАЕМ С ОБЪЕКТАМИ LOW POLY_//
    if len(low_array) == 1:
        obj = low_array[0]
        low_poly = create_object_copy(scene, obj, clear_materials=True)
    elif len(low_array) > 1:
        copied_objects = []
        for obj in low_array:
            obj_copy = create_object_copy(scene, obj, clear_materials=True)
            copied_objects.append(obj_copy)

        ignore_group(context, map_name, 'AO', copied_objects)
        bpy.ops.object.select_all(action='DESELECT')

        for obj in copied_objects:
            obj.select_set(True)
        
        bpy.context.view_layer.objects.active = copied_objects[0]
        bpy.ops.object.join()
        low_poly = bpy.context.active_object

    high_poly.name = "__" + single_collection.name + "_high_joined"
    low_poly.name = "__" + single_collection.name + "_low_joined"
    context.scene.xd_baker.attributes.bake_texture_name = single_collection.name
    return high_poly, low_poly

def fix_skew(context, lp_object):
    if context.scene.xd_baker.attributes.fix_skew and not context.scene.xd_baker.attributes.custom_cage_object:
        bpy.context.view_layer.objects.active = bpy.data.objects[lp_object.name]
        lp_object.select_set(True)
        
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
        bpy.ops.mesh.customdata_custom_splitnormals_add()

        subdivide = lp_object.modifiers.new(name="Subdivision", type='SUBSURF')
        subdivide.subdivision_type = 'SIMPLE'
        subdivide.show_only_control_edges = False
        subdivide.use_custom_normals = True
        subdivide.levels = context.scene.xd_baker.attributes.skew_precision

        bpy.ops.object.modifier_apply(modifier="Subdivision")

def combine_meshes(context, collection=None, map_name=""):
    scene = context.scene
    bake_type = scene.xd_baker.attributes.bake_type # single / collection
    
    if bake_type == 'OBJECTS':
        high_poly, low_poly = combine_couples(context, map_name)
        if high_poly == None or low_poly == None:
            context.scene.xd_baker.temp_things.bake_lp_obj = None
            context.scene.xd_baker.temp_things.bake_hp_obj = None
            return {'CANCELLED'}
    elif bake_type == 'COLLECTIONS':
        high_poly, low_poly = combine_collections(context, collection, map_name)
        if high_poly == None or low_poly == None:
            context.scene.xd_baker.temp_things.bake_lp_obj = None
            context.scene.xd_baker.temp_things.bake_hp_obj = None
            return {'CANCELLED'}
    
    lp_material = bpy.data.materials.new(name="__LP_mat")
    scene.xd_baker.temp_things.bake_lp_mat = lp_material
    lp_material.use_nodes = True
    
    low_poly.data.materials.append(lp_material)
    lp_node_tree = low_poly.data.materials[-1].node_tree
    
    pri_shader_node = get_node("BSDF_PRINCIPLED", lp_node_tree)
    
    if pri_shader_node is None:
        return {'CANCELLED'}
    
    fix_skew(context, low_poly)
    
    high_poly.hide_render = False
    low_poly.hide_render = False
    
    context.scene.xd_baker.temp_things.bake_lp_obj = low_poly
    context.scene.xd_baker.temp_things.bake_hp_obj = high_poly
    
    high_poly.select_set(True) # set selection
    bpy.context.view_layer.objects.active = low_poly # set active

def create_cage_object(context):
    """создание кейджа для запекания из low_poly объекта"""
    
    expand = context.scene.xd_baker.attributes.cage_extrusion
    bake_low_poly = context.scene.xd_baker.temp_things.bake_lp_obj
    
    cage_obj = bake_low_poly.copy()
    cage_obj.data = cage_obj.data.copy()
    
    bm = bmesh.new()
    bm.from_mesh(cage_obj.data)
    
    for v in bm.verts:
        v.co += v.normal * expand
    
    bm.to_mesh(cage_obj.data)
    bm.free()
    
    cage_obj.name = cage_obj.name.replace("_low_", "_cage_")
    context.scene.collection.objects.link(cage_obj)
    context.scene.xd_baker.temp_things.bake_cg_obj = cage_obj

def select_prebaked_objects(context):
    bake_low_poly = context.scene.xd_baker.temp_things.bake_lp_obj
    bake_high_poly = context.scene.xd_baker.temp_things.bake_hp_obj
    
    for obj in bpy.data.objects: obj.select_set(False)
    
    bpy.data.objects[bake_high_poly.name].select_set(True)
    bpy.context.view_layer.objects.active = bake_low_poly

def create_img_node(map_type, colorspace, use_alpha = False):
    scene = bpy.context.scene
    lp_material = scene.xd_baker.temp_things.bake_lp_mat
    lp_node_tree = lp_material.node_tree
    old_images = bpy.data.images
    
    settings = scene.render.image_settings
    settings.color_depth = '16'
    settings.file_format = 'TIFF'
    
    baked_texture_name = scene.xd_baker.attributes.bake_texture_name
    bt_name = baked_texture_name + "_" + map_type.lower()
    
    img_width = scene.xd_baker.attributes.img_bake_width
    img_height = scene.xd_baker.attributes.img_bake_height
    if scene.xd_baker.attributes.link_width_height: img_height = img_width
    
    img_node = lp_node_tree.nodes.new('ShaderNodeTexImage')
    baked_texture = None
    
    def new_image(im_name, width, height):
        baked_texture = bpy.data.images.new(im_name,
                                    width=width,
                                    height=height,
                                    alpha=use_alpha,
                                    float_buffer=True)
        baked_texture.colorspace_settings.name = colorspace
        baked_texture.name = im_name
        baked_texture.file_format = 'TIFF'
        return baked_texture
        
    if bt_name in old_images:
        baked_texture = bpy.data.images[bt_name]
        bpy.data.images.remove(baked_texture, do_unlink=True) # теперь я удаляю старую текстуру из памяти и создаю новую такую же пустую. Распаковка не требуется.
        baked_texture = new_image(bt_name, img_width, img_height)
    else:
        baked_texture = new_image(bt_name, img_width, img_height)
    
    img_node.image = baked_texture
    
    mat_nodes = lp_node_tree.nodes
    img_node.select = True
    mat_nodes.active = img_node
    
    scene.xd_baker.attributes.baked_texture = baked_texture

def clean_old_cache(temp_file_path): # чистим старые временные файлы
    temp_folder = os.path.dirname(temp_file_path)
    cur_temp_file = os.path.basename(temp_file_path)
    files = os.listdir(temp_folder)

    for file in files:
        if file.startswith("XD_Baker_") and file != cur_temp_file:
            os.remove(os.path.join(temp_folder, file))

def caching_image(context):
    baked_texture = context.scene.xd_baker.attributes.baked_texture
    
    # кэширование во временный файл. prefix нужен для отчистки старых файлов
    temp_file = tempfile.NamedTemporaryFile(delete=False, prefix="XD_Baker_", suffix=".tif")
    temp_file_path = temp_file.name
    context.scene.xd_baker.attributes.temp_file_path = temp_file_path
    
    clean_old_cache(temp_file_path)
    
    baked_texture.filepath_raw = temp_file_path
    
    if baked_texture.has_data:
        baked_texture.save()
        baked_texture.reload()
        baked_texture.update()
    else:
        pass

def numpy_to_blender_image(pixels_array, save_path):
    height, width, _ = pixels_array.shape
    
    # Создаем новое изображение в Blender
    image = bpy.data.images.new(
        name="ConvertedImage", 
        width=width, 
        height=height
    )

    # Преобразуем массив в линейный формат
    flat_pixels = pixels_array.flatten()
    
    # Загрузка пикселей в изображение
    image.pixels = flat_pixels
    
    # Сохранение изображения
    image.filepath = save_path
    image.save()

def load_image(temp_file_path):
    loaded_image = bpy.data.images.load(temp_file_path)
    loaded_image.reload()
    
    if loaded_image.has_data:
        loaded_image.update()
    
    return loaded_image

def image_to_array(image):
    return np.array(image.pixels).reshape((image.size[1], image.size[0], 4))

def array_to_image(image_data, float_buffer=True):
    height, width, channels = image_data.shape
    
    # Инициализация flat_pixels
    flat_pixels = None
    if float_buffer: # Нормализация значений пикселей
        flat_pixels = image_data.ravel()
        new_image = bpy.data.images.new(name="Processed Image", width=width, height=height, float_buffer=True)
        new_image.pixels = flat_pixels
    else:
        image_data = np.power(image_data, 1.0 / 2.2)
        image_data = np.clip(image_data, 0, 1)
        flat_pixels = image_data.ravel()
        new_image = bpy.data.images.new(name="Processed Image", width=width, height=height, float_buffer=False)
        new_image.pixels = flat_pixels
    return new_image
    
def save_image(image, file_path):
    # Путь и формат
    image.filepath_raw = file_path
    image.file_format = 'TIFF'

    # Сохранение
    image.save()
    image.update()
    image.reload()

def clean_image_data(image): # удаление изображение из памяти blender
    rem_image = bpy.data.images.get(image.name)
    bpy.data.images.remove(rem_image, do_unlink=True)

def convert_to_8bit(image_data): # Нормализация значений от 0 до 255
    converted_image = (image_data / 256).astype(np.uint8)
    return converted_image

def set_texture_addon_folder(context): # собираем путь для файла изображения
    baked_texture = context.scene.xd_baker.attributes.baked_texture
    dir_path = context.scene.xd_baker.attributes.bake_folder
    abspath = bpy.path.abspath(dir_path)
    final_path = abspath + baked_texture.name + '.tif'
    return final_path

def filtering_image(context, map_guid, map_depth):
    temp_file_path = context.scene.xd_baker.attributes.temp_file_path
    image = load_image(temp_file_path) # это будущий мусор, который надо чистить
    image_data = image_to_array(image)
    clean_image_data(image)
    
    if map_guid == 'Normal' and get_options_var(context, "Normal", "Dithering"):
        accuracy = get_options_var(context, "Normal", "Accuracy")
        image_data = filter_dithering(context, image_data, accuracy) # dithering
    
    filtered_image = array_to_image(image_data, True)
    
    save_image(filtered_image, temp_file_path)
    clean_image_data(filtered_image)
    image_data = None
    context.scene.xd_baker.attributes.baked_texture.reload()
    context.scene.xd_baker.attributes.baked_texture.pack() # если не паковать, то текстура затрется следующей запекаемой картой

def save_texture(context, collection=None, map_depth=8):
    temp_file_path = context.scene.xd_baker.attributes.temp_file_path
    image = load_image(temp_file_path)
    image_data = image_to_array(image)
    clean_image_data(image)
    
    baker_folder = set_texture_addon_folder(context)
    image = array_to_image(image_data, False)
    save_image(image, baker_folder)
    clean_image_data(image)
    image_data = None

def clear_template_things(context): # удаляем временно созданные объекты бейка
    temp_things = context.scene.xd_baker.temp_things
    for thing_name in dir(temp_things):
        if thing_name not in temp_things:
            continue
        
        if thing_name == "bake_cg_obj": # исключаем из удаления объект указанный в поле custom_cage_object
            if context.scene.xd_baker.temp_things.bake_cg_obj == context.scene.xd_baker.attributes.custom_cage_object:
                continue
        
        thing = getattr(temp_things, thing_name)

        if type(thing) is bpy.types.Object:
            bpy.data.objects.remove(thing, do_unlink=True)
        elif type(thing) is bpy.types.Material:
            bpy.data.materials.remove(thing, do_unlink=True)

def remove_materials(context): # удаляем временно созданные материалы
    scene = context.scene
    lp_material = scene.xd_baker.temp_things.bake_lp_mat
    hp_material = scene.xd_baker.temp_things.bake_hp_mat
    
    if lp_material is not None:
        bpy.data.materials.remove(lp_material, do_unlink=True)
    if hp_material is not None:
        bpy.data.materials.remove(hp_material, do_unlink=True)

def shading(viewport_camera, vertex, channel):
    # шейдинг каждого цветового канал отдельно (для кейджа)
    direction = (viewport_camera - vertex.co).normalized()
    shading = (vertex.normal.dot(direction) + 0.5)  * channel
    return shading

def generate_gpu_cage(object, color, extrusion, depth_test, blend_set):
    """Генерация кейджа для gpu рендера. Отображение цветного полупрозрачного информационного кейджа"""
    gpu.state.depth_test_set(depth_test)
    gpu.state.face_culling_set('BACK')
    gpu.state.front_facing_set(False)
    gpu.state.depth_mask_set(True)
    gpu.state.blend_set(blend_set)
    
    object_pos = object.location
    mesh = object.data
    
    vertices = np.empty((len(mesh.vertices), 3), 'f')
    indices = np.empty((len(mesh.loop_triangles), 3), 'i')
    
    mesh.vertices.foreach_get("co", np.reshape(vertices, len(mesh.vertices) * 3))
    mesh.loop_triangles.foreach_get("vertices", np.reshape(indices, len(mesh.loop_triangles) * 3))
    
    # позиция камеры вьюпорта
    viewport_camera = bpy.context.region_data.view_matrix.inverted().to_translation()
    viewport_camera[2] += 0.1
    
    vertices = [vertex.co + object_pos + (vertex.normal * extrusion) for vertex in mesh.vertices]
    shaded_colors = [(shading(viewport_camera, vertex, color[0]), shading(viewport_camera, vertex, color[1]), shading(viewport_camera, vertex, color[2]), color[3]) for vertex in mesh.vertices]
    shader = gpu.shader.from_builtin('SMOOTH_COLOR', config = 'CLIPPED')
    #shader = gpu.shader.uniform_float("color", (1.0, 0.0, 0.5, 0.5))
    
    batch = batch_for_shader(shader, 'TRIS', {"pos": vertices, "color": shaded_colors}, indices=indices)
    batch.draw(shader)

def draw_low_gpu_cage(): # основной кейдж
    scene = bpy.context.scene
    if scene.xd_baker.attributes.custom_cage_object: return # если в качестве кейджа кастомный объект
    if not scene.xd_baker.attributes.show_cage: return # если кейдж выключен
    
    expand = scene.xd_baker.attributes.cage_extrusion
    opacity = scene.xd_baker.attributes.cage_opacity
    color = (0.0, 1.0, 0.0, opacity)
    bake_type = scene.xd_baker.attributes.bake_type
    
    if bake_type == "OBJECTS":
        if scene.xd_baker.attributes.apply_modifiers:
            low_poly_obj = bpy.data.objects[scene.xd_baker.attributes.low_poly_obj.name]
        else:
            low_poly_obj = scene.xd_baker.attributes.low_poly_obj
        
        if low_poly_obj is None: return
        generate_gpu_cage(low_poly_obj, color, expand, 'LESS_EQUAL', 'ALPHA')
    
    elif bake_type == "COLLECTIONS":
        for idx, group in enumerate(scene.xd_baker.attributes.my_collection.group):
            if group.name == "": continue # пропускаем пустые элементы списка
            real_collection = bpy.data.collections[group.name] # реальная коллекция
            coll_color = (cage_colors[idx][0], cage_colors[idx][1], cage_colors[idx][2], opacity)
            for obj in real_collection.all_objects:
                if not obj.name.lower().endswith("_low"):
                    continue
                generate_gpu_cage(obj, coll_color, expand, 'LESS_EQUAL', 'ALPHA')
    
    

def draw_high_gpu_cage(): # вспомогательный кейдж для отображения пересечения кейджа с high poly
    color = (1.0, 0.0, 0.0, 1.0)
    scene = bpy.context.scene
    if scene.xd_baker.attributes.custom_cage_object: return # если в качестве кейджа кастомный объект
    if not scene.xd_baker.attributes.show_cage or not scene.xd_baker.attributes.high_mask: return # если кейдж выключен или выключен красный кейдж
    
    bake_type = scene.xd_baker.attributes.bake_type
    
    if bake_type == "OBJECTS":
        if scene.xd_baker.attributes.apply_modifiers:
            high_poly_obj = bpy.data.objects[scene.xd_baker.attributes.high_poly_obj.name + "#gpu#mask"]
        else:
            high_poly_obj = scene.xd_baker.attributes.high_poly_obj
        
        if high_poly_obj is None: return
        generate_gpu_cage(high_poly_obj, color, 0.001, 'LESS_EQUAL', 'NONE')
        
    elif bake_type == "COLLECTIONS":
        for group in scene.xd_baker.attributes.my_collection.group:
            if group.name == "": continue # пропускаем пустые элементы списка
            real_collection = bpy.data.collections[group.name] # реальная коллекция
            
            if scene.xd_baker.attributes.apply_modifiers:
                for obj in real_collection.all_objects:
                    #if not obj.name.lower().endswith("_high#gpu#cage"): continue # пропускаем все НЕ high poly объекты
                    if obj.name + "#gpu#mask" in bpy.data.objects:
                        
                        cg_obj = bpy.data.objects[obj.name + "#gpu#mask"]
                        generate_gpu_cage(cg_obj, color, 0.001, 'LESS_EQUAL', 'NONE')
            else:
                for obj in real_collection.all_objects:
                    if not obj.name.lower().endswith("_high"): continue # пропускаем все НЕ high poly объекты
                    generate_gpu_cage(obj, color, 0.001, 'LESS_EQUAL', 'NONE')

def prepare_temp_material(): # создаем временный материал
    template_material = bpy.data.materials.new(name="override_mat")
    bpy.context.scene.view_layers[0].material_override = template_material
    template_material.use_nodes = True
    nodes = template_material.node_tree.nodes
    principled = nodes.get('Principled BSDF')
    nodes.remove(principled)
    return nodes, template_material

def bake_temp_material(override_mat, cage_object, use_selected_to_active=True): # печем
    bpy.ops.object.bake(type="DIFFUSE",
                        use_selected_to_active=use_selected_to_active,
                        use_cage=True,
                        cage_object=cage_object,
                        margin=0,
                        pass_filter=set({'COLOR'})
                        )
    bpy.data.materials.remove(override_mat) # удаляем временный материал

def get_options_var(context, map_name, option): # забираем значение свойства опции по типу
    options = context.scene.xd_baker.attributes.bake_maps_group.maps_group[map_name].options
    data_type = options[option].type

    if data_type == 'BOOL':
        return options[option].bool_value
    elif data_type == 'INT':
        return options[option].int_value
    elif data_type == 'FLOAT':
        return options[option].float_value
    elif data_type == 'STRING':
        return options[option].string_value
    elif data_type == 'ENUM':
        return options[option].enum_value
    else:
        return None

def get_selected_maps_cnt(context): # вернет количество активированных для бейка карт
    maps = context.scene.xd_baker.attributes.bake_maps_group.maps_group
    enabled_arr = []
    for m in maps:
        if not m.enabled:
            continue
        enabled_arr.append(m.name)
    return len(enabled_arr)

def update_desgraph(): # насильное обновление графа. Используется при удалении коллекции для скрытия кнопки Bake Maps
    selected_objects = bpy.context.selected_objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in selected_objects:
        obj.select_set(True)