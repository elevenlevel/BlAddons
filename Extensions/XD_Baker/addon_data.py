from bpy.props import StringProperty, IntProperty, FloatProperty, BoolProperty, EnumProperty, PointerProperty, CollectionProperty, FloatVectorProperty
from bpy.types import PropertyGroup, Object, Material, Image



# список карт
bake_maps_list = {"Diffuse": {"unfolded":False, "enabled":False, "colorspace":'sRGB', "alpha":False, "depth":8, "options":{
                                                                                                                                                "Albedo":{"type":"BOOL", "value":True}
                                                                                                                                                }},
                  "AO": {"unfolded":False, "enabled":False, "colorspace":'Non-Color', "alpha":False, "depth":8, "options":{
                                                                                                                                                "Inside":{"type":"BOOL", "value":False},
                                                                                                                                                "Only Local":{"type":"BOOL", "value":True},
                                                                                                                                                "Samples":{"type":"INT", "value":16},
                                                                                                                                                "Distance":{"type":"FLOAT", "value":0.1},
                                                                                                                                                "Ignore Group":{"type":"BOOL", "value":False}
                                                                                                                                                }},
                  "Normal": {"unfolded":False, "enabled":False, "colorspace":'Non-Color', "alpha":False, "depth":8, "options":{
                                                                                                                                                "Invert Green":{"type":"BOOL", "value":False},
                                                                                                                                                "Dithering":{"type":"BOOL", "value":False},
                                                                                                                                                "Accuracy":{"type":"FLOAT", "value":16.0}
                                                                                                                                                }},
                  "Normal os": {"unfolded":False, "enabled":False, "colorspace":'Non-Color', "alpha":False, "depth":16, "options":{
                                                                                                                                                }},
                  "Position": {"unfolded":False, "enabled":False, "colorspace":'Non-Color', "alpha":False, "depth":16, "options":{
                                                                                                                                                }},
                  "Roughness": {"unfolded":False, "enabled":False, "colorspace":'Non-Color', "alpha":False, "depth":8, "options":{
                                                                                                                                                }},
                  "Emission": {"unfolded":False, "enabled":False, "colorspace":'sRGB', "alpha":False, "depth":8, "options":{
                                                                                                                                                }},
                  "Curvature": {"unfolded":False, "enabled":False, "colorspace":'Non-Color', "alpha":False, "depth":8, "options":{
                                                                                                                                                }},
                  "Edge Wear": {"unfolded":False, "enabled":False, "colorspace":'Non-Color', "alpha":False, "depth":8, "options":{
                                                                                                                                                "Samples":{"type":"INT", "value":16},
                                                                                                                                                "Strength":{"type":"FLOAT", "value":0.1}
                                                                                                                                                }},
                  "Vertex Color": {"unfolded":False, "enabled":False, "colorspace":'sRGB', "alpha":False, "depth":8, "options":{
                                                                                                                                                "Attribute":{"type":"STRING", "value":"Color"}
                                                                                                                                                }},
                  "Height": {"unfolded":False, "enabled":False, "colorspace":'Non-Color', "alpha":False, "depth":16, "options":{
                                                                                                                                                }},
                  "Opacity": {"unfolded":False, "enabled":False, "colorspace":'Non-Color', "alpha":True, "depth":8, "options":{
                                                                                                                                                "SDF Shrinked":{"type":"BOOL", "value":False},
                                                                                                                                                "SDF Expanded":{"type":"BOOL", "value":False},
                                                                                                                                                }},
                  "Custom": {"unfolded":False, "enabled":False, "colorspace":'Non-Color', "alpha":False, "depth":16, "options":{
                                                                                                                                                }},
                  "UV Wire": {"unfolded":False, "enabled":False, "colorspace":'Non-Color', "alpha":False, "depth":8, "options":{
                                                                                                                                                "UV Map":{"type":"INT", "value":0},
                                                                                                                                                "UDIM":{"type":"BOOL", "value":False}
                                                                                                                                                }},                                                                                                                              
                 }

cage_colors = [
                (0.552, 0.666, 0.796), (0.733, 0.847, 0.329), (1.0, 0.850, 0.184), (0.4, 0.760, 0.588),
                (0.898, 0.713, 0.580), (0.905, 0.541, 0.823), (0.701, 0.701, 0.701), (0.650, 0.847, 0.890),
                (0.670, 0.913, 0.737), (0.105, 0.490, 0.611), (0.301, 0.654, 0.254), (0.768, 0.698, 0.839),
                (0.0, 0.674, 0.674), (0.745, 0.423, 0.172), (0.411, 0.329, 0.588), (0.313, 0.627, 0.941),
                (0.941, 0.627, 0.313), (1.0, 0.286, 1.0), (1.0, 0.0, 0.513), (1.0, 0.929, 0.0)
              ]



object_render_status = {}
object_selection_status = {}
object_active_status = {}

# Список с выбором типа бейка
bake_options = [('OBJECTS', 'Any Objects Selection', "Put Objects in the appropriate fields"),
                ('COLLECTIONS', 'Collections _high/_low', "Put Collection. Baker will match the names automatically")]

class PropItem(PropertyGroup):
    name : StringProperty() # type: ignore
    index : IntProperty() # type: ignore
    icon : StringProperty(default="OUTLINER_COLLECTION") # type: ignore


class PropGroup(PropertyGroup):
    group : CollectionProperty(type=PropItem) # type: ignore

class EnumItem(PropertyGroup): # один элемент саиска типа ENUM вместо EnumProperty
    name : StringProperty() # type: ignore


class BakeMapOptItem(PropertyGroup): # дополнительные параметры каждой карты
    name : StringProperty() # type: ignore
    type : StringProperty(default="BOOL") # type: ignore # BOOL FLOAT INT STRING ENUM

    bool_value : BoolProperty(default=False) # type: ignore
    int_value : IntProperty(default=0) # type: ignore
    float_value : FloatProperty(default=0.0) # type: ignore
    string_value : StringProperty(default="") # type: ignore
    enum_value : EnumProperty(name="enum", description="", items=[]) # type: ignore

class BakeMapItem(PropertyGroup): # класс с картами и их свойствами
    name : StringProperty() # type: ignore
    unfolded : BoolProperty(default=False) # type: ignore # стрелка сворачивания/разворачивания опций карты
    enabled : BoolProperty(default=False) # type: ignore # чекбокс включения запекания карты
    colorspace : StringProperty() # type: ignore
    alpha : BoolProperty() # type: ignore
    depth : IntProperty() # type: ignore
    options : CollectionProperty(type=BakeMapOptItem) # type: ignore # дополнительные параметры каждой карты


class BakeMapsGroup(PropertyGroup):
    maps_group : CollectionProperty(type=BakeMapItem) # type: ignore


class XDBakerAttributes(PropertyGroup): # атрибуты используемые аддоном
    my_collection : PointerProperty(type=PropGroup) # type: ignore
    bake_type : EnumProperty(items=bake_options, name="Bake Type") # type: ignore
    fix_skew : BoolProperty(default=False, description="Automatic fix Skew") # type: ignore
    skew_precision : IntProperty(default=4, description="Steps of fixing Skew") # type: ignore
    low_poly_obj : PointerProperty(type=Object) # type: ignore
    high_poly_obj : PointerProperty(type=Object) # type: ignore
    low_poly_array : PointerProperty(type=Object) # type: ignore
    custom_cage_object : PointerProperty(type=Object, description="An external Object as a Cage") # type: ignore
    lp_material : PointerProperty(type=Material) # type: ignore
    hp_material : PointerProperty(type=Material) # type: ignore
    baked_texture : PointerProperty(type=Image) # type: ignore #TODO: возможно стоит перенести в temp_things
    enable_save : BoolProperty(name="enable_save", description="Enable saving baked Images", default=False) # type: ignore
    ignore_group : BoolProperty(name="ignore_group", description="Ignore Overlapping of Objects", default=False) # type: ignore
    bake_folder : StringProperty(subtype='DIR_PATH', default = "//", description="Path to folder for save textures") # type: ignore
    img_bake_width  : IntProperty(name="Image Width",  description="Width of image to bake", default=2048) # type: ignore
    img_bake_height : IntProperty(name="Image Height", description="Height of image to bake", default=2048) # type: ignore
    link_width_height : BoolProperty(name="Link Width/Height", description="Link Width/Height", default=True) # type: ignore
    img_bake_margin : IntProperty(name="Padding", description="Image Padding", default=8) # type: ignore
    cage_extrusion : FloatProperty(name="Cage Extrusion", description="Cage Extrusion", default=0.1, soft_min=0.0) # type: ignore
    bake_maps_group : PointerProperty(type=BakeMapsGroup) # type: ignore

    show_cage : BoolProperty(name="Show Cage", description="Show Cage", default=False) # type: ignore
    high_mask : BoolProperty(name="High Mask", description="Draw a red mask when the high poly object's cage intersects", default=False) # type: ignore
    cage_opacity : FloatProperty(name="Cage Opacity", description="Cage Opacity", default=0.5, min=0.0, max=1.0, precision=2) # type: ignore
    apply_modifiers : BoolProperty(name="Apply Modifiers", description="Apply Modifiers (Beta)", default=False) # type: ignore
    is_baking : BoolProperty(default=False) # type: ignore
    temp_file_path : StringProperty() # type: ignore

    bake_texture_name : StringProperty() # type: ignore # имя текстуры в которую идет запекание


class XDBakerBackup(PropertyGroup): # бэкап значений для восстановления после запекания
    old_engine : StringProperty() # type: ignore # состояние параметра render_engine до запекания
    old_device : StringProperty() # type: ignore # состояние параметра device до запекания
    old_bake_maps_list : StringProperty(default="") # type: ignore # старый список параметров для сравнения при инициализации


class XDBakerTempThings(PropertyGroup):
    gpu_cg_objs : PointerProperty(type=Object) # type: ignore
    bake_cg_obj : PointerProperty(type=Object) # type: ignore
    bake_lp_obj : PointerProperty(type=Object) # type: ignore
    bake_hp_obj : PointerProperty(type=Object) # type: ignore
    bake_lp_mat : PointerProperty(type=Material) # type: ignore
    bake_hp_mat : PointerProperty(type=Material) # type: ignore


class XDBakerAlertUi(PropertyGroup):
    low_poly_obj_ui : BoolProperty(default=False) # type: ignore
    high_poly_obj_ui : BoolProperty(default=False) # type: ignore
    bake_maps_button_ui : BoolProperty(default=False) # type: ignore


class XDBaker(PropertyGroup):
    attributes : PointerProperty(type=XDBakerAttributes) # type: ignore # основные атрибуты аддона
    backup : PointerProperty(type=XDBakerBackup) # type: ignore # бэкап значений для восстановления после запекания
    temp_things : PointerProperty(type=XDBakerTempThings) # type: ignore # вспомогшательные объекты, создаваемые в процессе работы аддона
    alert_ui : PointerProperty(type=XDBakerAlertUi) # type: ignore # UI для вывода сообщений
    # Удалил maps т.к. это уже есть в свойстве bake_maps_group класса XDBakerAttributes


data_classes = [
    PropItem,
    PropGroup,
    EnumItem,
    BakeMapOptItem,
    BakeMapItem,
    BakeMapsGroup,
    XDBakerAttributes,
    XDBakerBackup,
    XDBakerTempThings,
    XDBakerAlertUi,
    XDBaker
    ]
