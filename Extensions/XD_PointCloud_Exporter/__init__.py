import bpy, os

from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatProperty,
    IntProperty,
    EnumProperty,
    CollectionProperty,
    PointerProperty,
)
from bpy_extras.io_utils import (
    ExportHelper,
)

from .xdpc_panels import panel_classes
from .xdpc_functions import *
from bpy.app.handlers import persistent

class InstanceListItem(bpy.types.PropertyGroup):
    def update_instance(self, context):
        print("update_instance")
        if self.instance:
            #print("self.instance: ", self.instance.name)
            #self.name = self.instance.name
            #append_instance(self, context, self.emitter.name)
            pass
        else:
            #print("self.name: ", self.name)
            #remove_instance(self, context, self.name)
            pass
    
    name : StringProperty(default="") # type: ignore
    index : IntProperty(default=0) # type: ignore
    type : StringProperty(default="ADD") # type: ignore
    enabled : BoolProperty(default=True) # type: ignore
    factor : IntProperty(name="Factor", default=0) # type: ignore
    factor_result : FloatProperty(name="Factor", default=0.0) # type: ignore # ЭТО ОТВЕЧАЕТ ЗА ВЫБОРКУ ИНСТАНСОВ ПО ТОЧКАМ
    instance : PointerProperty(type=bpy.types.Object, update=update_instance) # type: ignore


class EmitterListItem(bpy.types.PropertyGroup):
    def update_emitter(self, context):
        # TODO: пока убираем возможность дважды добавлять один объект в качестве эмиттеров
        # TODO: добавляем свойство postfix которое будет добавляться в конец имени объекта и которое не будет изменяться при ресорте эмиттеров
        if self.emitter:
            print("update_emitter")
            # при попытке создать эмиттер из объекта который уже используется как эмиттер - игнорим эту попытку
            emit_list = bpy.context.scene.xdpc_attributes.emit_list
            names = [e.name for e in emit_list]
            names_count = count_list_elements(names)

            if self.emitter.name != "" and self.emitter.name in names:
                name_cnt = names_count[self.emitter.name]
                if name_cnt > 1:
                    self.emitter = None # сбрасываем текущий эмиттер
                    return
            
            emitter = self.emitter
            self.name = emitter.name
            #set_emitters_postfix(self)
            
            if self.emitter_collection:
                collection_objects = self.emitter_collection.all_objects
                
                append_emitter(self, context, self.emitter.name)
                set_modifier_fields(self)
                
                for idx, obj in enumerate(collection_objects):
                    new_inst_item = self.inst_list.add()
                    new_inst_item.index = idx
                    new_inst_item.name = obj.name
            else:
                self.inst_list.clear()
                self.inst_idx = 0
        else:
            remove_emitter_object(self.name)

            if self.type != "ADD":
                unname_emitter_item(self.index)
    
    emitter_collection : bpy.props.PointerProperty(type=bpy.types.Collection, update=update_emitter) # type: ignore
    name : StringProperty(default="") # type: ignore
    postfix : IntProperty(default=-1) # type: ignore
    index : IntProperty(default=0) # type: ignore
    type : StringProperty(default="ADD") # type: ignore
    enabled : BoolProperty(default=True) # type: ignore
    emitter : PointerProperty(type=bpy.types.Object, update=update_emitter) # type: ignore
    inst_list : CollectionProperty(type=InstanceListItem) # type: ignore
    inst_idx : IntProperty(default=0) # type: ignore


class SceneObjectsItem(bpy.types.PropertyGroup):
    object : PointerProperty(type=bpy.types.Object) # type: ignore


class XDPC_Attributes(bpy.types.PropertyGroup):
    emit_idx : IntProperty(default=0) # type: ignore
    emit_list : CollectionProperty(type=EmitterListItem) # type: ignore
    active_index: IntProperty(default=0) # type: ignore
    all_scene_objects : CollectionProperty(type=SceneObjectsItem) # type: ignore


def create_collection(collection_name, icon_value):
    # создаем техническую коллекцию для импортируемого объекта
    new_collection = bpy.data.collections.new(collection_name)
    
    if bpy.context.scene:
        bpy.context.scene.collection.children.link(new_collection)
    else:
        bpy.context.blend_data.collections.link(new_collection)
    
    new_collection.color_tag = icon_value
    #print(dir(new_collection))
    return new_collection


def append_emitter(self, context, instance_name):
    """Импорт объекта с geometry nodes из blend файла"""
    
    # создание рабочей коллекции для импортируемого объекта
    if not bpy.data.collections.get("XD_PROXY_COLLECTION"):
        scatter_collection = create_collection("XD_PROXY_COLLECTION", "COLOR_03")
    else:
        scatter_collection = bpy.data.collections.get("XD_PROXY_COLLECTION")
    
    directory = os.path.dirname(__file__)
    blendfile = os.path.join(directory, "scatter.blend")
    section   = "\\Object\\"
    object    = "XD_SCATTER"
    directory = blendfile + section
    
    # непосредственно импорт объекта
    with bpy.data.libraries.load(blendfile, link=False) as (data_from, data_to):
        data_to.objects = [ob for ob in data_from.objects if ob == object]
    
    # линковка объекта в коллекцию
    if data_to.objects:
        obj = data_to.objects[0]
        obj.name = "XD_SCATTER_" + instance_name
        scatter_collection.objects.link(obj)

"""
СОБЫТИЯ
Емиттеры:
1. Нажатие - у емиттера
    • emitter.rem_item
    • очистка инстансов у текущего индекса эмиттера
2. Нажатие х у емиттера
    • выполняется update_addon
    • удаление инстансов у текущего индекса эмиттера
3. Удаление объекта емиттера
    • в update проверка эмиттеров на пустое имя
    • если имя пустое, удаление инстансов у текущего индекса эмиттера
4. Переименование емиттера

Инстансы:
1. 
2. 



"""



@persistent 
def update_addon(scene):
    print("update_addon")
    add_empty_emitter()
    recalc_instances_factors()
    #remove_emitter_when_object_deleted()
    remove_empty_proxy_collection()
    update_instances_when_object_changed()
    # clean_instances_of_empty_emitter() # закомментировано т.к. инстансы лучше оставлять для замены эмиттера
    sort_emitters_indices()
    reset_active_index()

@persistent 
def initialize_addon(scene): # инициализация аддона
    remove_empty_proxy_collection()
    add_empty_emitter()
    reset_active_index()

    # при инициализации заполняем all_scene_objects для проверок
    bpy.context.scene.xdpc_attributes.all_scene_objects.clear()
    for obj in bpy.data.objects:
        new_bkp_object = bpy.context.scene.xdpc_attributes.all_scene_objects.add()
        new_bkp_object.object = obj



class XD_ExportXDPC(bpy.types.Operator, ExportHelper):
    """Write a XDPC file"""
    bl_idname = "xd_export_scene.xdpc"
    bl_label = "Export PointCloud"
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = ".xdpc"
    filter_glob: StringProperty(default="*.xdpc", options={'HIDDEN'}) # type: ignore

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.

    use_selection: BoolProperty(
        name="Selected Objects",
        description="Export selected and visible objects only",
        default=True,
    ) # type: ignore
    use_visible: BoolProperty(
        name='Visible Objects',
        description='Export visible objects only',
        default=False
    ) # type: ignore
    use_active_collection: BoolProperty(
        name="Active Collection",
        description="Export only objects from the active collection (and its children)",
        default=False,
    ) # type: ignore
    collection: StringProperty(
        name="Source Collection",
        description="Export only objects from this collection (and its children)",
        default="",
    ) # type: ignore
    data_types: EnumProperty(
        name="Include Data",
        options={'ENUM_FLAG'},
        items=(('POSITION', "Position", "Position of vertices"),
               ('NORMAL', "Normal", "Normals"),
               ('TANGENT', "Tangent", "Direction"),
               ('COLOR', "Color", "Vertex Color"),
               ('UV', "Uv", "UV coordinates"),
               ('CPROPS', "Custom Properties", "Custom Properties"),
               ),
        description="Which kind of object to export",
        default={'POSITION', 'NORMAL', 'TANGENT', 'COLOR'},
    ) # type: ignore

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        # Are we inside the File browser
        is_file_browser = context.space_data.type == 'FILE_BROWSER'
        #print("is_file_browser: ", is_file_browser)

        export_main(layout, self, is_file_browser)
        export_panel_include(layout, self, is_file_browser)

    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")
        
        keywords = self.as_keywords(ignore=("check_existing",
                                            "filter_glob",
                                            "ui_tab",
                                            ))
        #print("EXECUTE", self.filepath)
        from . import export_xdpc_bin
        return export_xdpc_bin.save(self, context, **keywords)


def export_main(layout, operator, is_file_browser):
    row = layout.row(align=True)

    if is_file_browser:
        row = layout.row(align=True)
        sub = row.row(align=True)


def export_panel_include(layout, operator, is_file_browser):
    header, body = layout.panel("FBX_export_include", default_closed=False)
    header.label(text="Include")
    if body:
        sublayout = body.column(heading="Limit to")
        if is_file_browser:
            sublayout.prop(operator, "use_selection")
            sublayout.prop(operator, "use_visible")
            sublayout.prop(operator, "use_active_collection")

        body.column().prop(operator, "data_types")


class XD_IO_FH_xdpc(bpy.types.FileHandler): # отвечает за пункт меню в коллекции
    bl_idname = "XD_IO_FH_xdpc"
    bl_label = "XD PointCloud"
    bl_export_operator = "xd_export_scene.xdpc"
    bl_file_extensions = ".xdpc"

    @classmethod
    def poll_drop(cls, context):
        #return poll_file_object_drop(context)
        return {'FINISHED'}


def menu_func_export(self, context):
    self.layout.operator(XD_ExportXDPC.bl_idname, text="XD PointCloud (.xdpc)")


classes = (
    *panel_classes,
    InstanceListItem,
    EmitterListItem,
    SceneObjectsItem,
    XDPC_Attributes,
    XD_ExportXDPC,
    XD_IO_FH_xdpc,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.app.handlers.load_post.append(initialize_addon)
    bpy.app.handlers.depsgraph_update_post.append(update_addon)
    bpy.types.Scene.xdpc_attributes = bpy.props.PointerProperty(type=XDPC_Attributes)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.app.handlers.depsgraph_update_post.remove(update_addon)
    bpy.app.handlers.load_post.remove(initialize_addon)
    del bpy.types.Scene.xdpc_attributes


if __name__ == "__main__":
    register()
