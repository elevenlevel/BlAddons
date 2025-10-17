import bpy
from bpy.types import Panel
from .utils.functions import is_collection
from .utils.functions import *

class XD_PT_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Objects"
    bl_category = "XD Baker"
    
    @classmethod
    def poll(cls, context):
        scene = bpy.context.scene
        my_collection = scene.xd_baker.attributes.my_collection
        group = my_collection.group

        if len(group) > 0 and group[-1].name != "":
            count = len(group)
            item = my_collection.group.add()
            item.name = ""

            if len(group) > 1:
                item.index = count
            else:
                item.index = 0
        return True
    
    # def __init__(self):
    #     scene = bpy.context.scene
    #     my_collection = scene.xd_baker.attributes.my_collection
    #     group = my_collection.group

    #     if len(group) > 0 and group[-1].name != "":
    #         count = len(group)
    #         item = my_collection.group.add()
    #         item.name = ""

    #         if len(group) > 1:
    #             item.index = count
    #         else:
    #             item.index = 0

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        xd_baker = scene.xd_baker

        row = layout.row()
        row.prop(scene.xd_baker.attributes, "bake_type", text="")
        selected_option = scene.xd_baker.attributes.bake_type
        box = layout.box()

        if selected_option == 'OBJECTS':
            row = box.row()
            row.alert = xd_baker.alert_ui.high_poly_obj_ui
            split = row.split(factor=0.4, align=True)
            col = split.column()
            col.label(text='High Poly')
            col = split.column()
            col.prop(scene.xd_baker.attributes, "high_poly_obj", text="")
            row = box.row()
            row.alert = xd_baker.alert_ui.low_poly_obj_ui
            split = row.split(factor=0.4, align=True)
            col = split.column()
            col.label(text='Low Poly')
            col = split.column()
            col.prop(scene.xd_baker.attributes, "low_poly_obj", text="")

        elif selected_option == 'COLLECTIONS':
            my_collection = scene.xd_baker.attributes.my_collection

            if len(my_collection.group)==0:
                row = box.row()
                bpy.props.index = 0
            else:
                for index, collection in enumerate(my_collection.group):
                    item = my_collection.group[index]
                    
                    row = box.row()
                    column = row.column()
                    
                    if item.name != "":
                        collection_icon = 'OUTLINER_COLLECTION' # обычный значек

                        layer_collection = context.view_layer.layer_collection.children[item.name]
                        if layer_collection.exclude:
                            collection_icon = 'COLLECTION_COLOR_07' # серенький значек
                    else:
                        collection_icon = 'OUTLINER_OB_GROUP_INSTANCE'

                    
                    column.prop(item, "name", text="", icon=collection_icon)
                    
                    if not is_collection(context):
                        # прячем поле если выбранный объект не коллекция
                        column.enabled = False
                    
                    column = row.column()
                    if index < len(my_collection.group) - 1:
                        column.operator("my.remove_item", text="", icon='REMOVE').index = item.index
                    else:
                        row.label(icon='BLANK1')
                
        row = layout.row()
        column = row.column()
        column.prop(scene.xd_baker.attributes, "enable_save", text="")

        enabled = False
        if scene.xd_baker.attributes.enable_save:
            enabled = True

        column_a = row.column()
        column_a.prop(scene.xd_baker.attributes, "bake_folder", text='')
        column_a.enabled = enabled
        column = row.column()
        column.operator('scene.open_folder_op', text='', icon='MENU_PANEL')
        
        row = layout.row()
        box = row.box()
        box.enabled = not xd_baker.alert_ui.bake_maps_button_ui
        box.operator('object.bake_op', text='Bake Maps', icon='MOD_DYNAMICPAINT')


class XD_PT_Images_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Images"
    bl_category = "XD Baker"

    def super_row(self, box, ui_x=1.0, ui_y=0.65, sep_factor=1.0):
        row = box.row(align=True)
        row.label(icon="BLANK1")
        row.ui_units_x = ui_x
        row.ui_units_y = ui_y
        return row
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        col1 = row.column()
        col2 = row.column()
        col3 = row.column()
        col1.prop(scene.xd_baker.attributes, "img_bake_width", text="W:")
        col2.prop(scene.xd_baker.attributes, "link_width_height", text="", icon="LINKED")
        if scene.xd_baker.attributes.link_width_height:
            col3.prop(scene.xd_baker.attributes, "img_bake_width", text="H:")
            col3.enabled = False
        else:
            col3.prop(scene.xd_baker.attributes, "img_bake_height", text="H:")

        row = layout.row()
        row.prop(scene.xd_baker.attributes, "img_bake_margin", text="Padding")
        
        box = layout.box()
        bpy.context.view_layer.update()
        box.scale_y = 0.65

        bake_maps_group = scene.xd_baker.attributes.bake_maps_group.maps_group

        for iter in bake_maps_group:
            map_name = iter.name
            map_unfolded = iter.unfolded
            map_enabled = iter.enabled
            map_cspace = iter.colorspace
            map_alpha = iter.alpha
            map_depth = iter.depth
            map_options = iter.options

            row = box.row()

            if len(map_options) > 0: # рисуем стрелку сворачивания группы только если карта имеет дополнительнце опции
                icon='TRIA_DOWN' if map_unfolded else 'TRIA_RIGHT'
            else:
                icon='DOT'
            
            row.prop(iter, "unfolded", text=map_name, icon=icon, emboss=False, toggle=False) # стрелка сворачивания группы
            row.prop(iter, "enabled", text="", toggle=False) # чекбокс включения/выключание текущей карты
            
            if map_unfolded:
                for opt in map_options:
                    row = self.super_row(box)
                    if opt.type == "BOOL":
                        row.prop(opt, "bool_value", text=opt.name)
                    elif opt.type == "INT":
                        row.prop(opt, "int_value", text=opt.name)
                    elif opt.type == "FLOAT":
                        row.prop(opt, "float_value", text=opt.name)
                    elif opt.type == "STRING":
                        row.prop(opt, "string_value", text=opt.name)
                    elif opt.type == "ENUM": # ЭТО СЕЙЧАС НЕ РАБОТАЕТ ИЗ-ЗА СЛОЖНОСТИ С ЗАПОЛНЕНИЕМ EnumProperty ЗНАЧЕНИЯМИ ИЗ СПИСКА bake_maps_list
                        #row.prop(opt, "enum_value", text=opt.name)
                        #row.prop(opt, "enum_value")
                        row.prop(opt, "enum_value", text="")
        box.separator(factor=0.1)


class XD_PT_Cage_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Cage"
    bl_category = "XD Baker"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        main_cage_box = layout.box()
        row = main_cage_box.row()
        column = row.column()
        column.prop(scene.xd_baker.attributes, "show_cage", text="Cage", toggle=False)
        column_a = row.column()
        column_a.prop(scene.xd_baker.attributes, "high_mask", text="Mask", toggle=False)
        
        row = main_cage_box.row()
        column_b = row.column()
        column_b.prop(scene.xd_baker.attributes, "cage_opacity", text="Opacity", slider=True)
        column_c = row.column()
        row_c = column_c.row()
        row_c.label(text="Apply Modifiers")
        row_c.operator('object.apply_cage_modifiers', text='', emboss=False, icon='CHECKBOX_HLT' if scene.xd_baker.attributes.apply_modifiers else 'CHECKBOX_DEHLT')

        if not scene.xd_baker.attributes.show_cage:
            column_a.enabled = False
            column_b.enabled = False
            column_c.enabled = False
        
        row = main_cage_box.row()
        row.prop(scene.xd_baker.attributes, "cage_extrusion", text="Extrusion")

        row = main_cage_box.row()
        row.prop(context.scene.render.bake, "max_ray_distance", text="Max Ray Distance")

        row = main_cage_box.row()
        row.prop(scene.xd_baker.attributes, "fix_skew", text="Fix Skew")
        row.prop(scene.xd_baker.attributes,"skew_precision", text="Skew Precision")
        main_cage_box.enabled = scene.xd_baker.attributes.custom_cage_object == None # прячем параметры если custom cage указан

        split_row = layout.row()
        split_row.separator()

        custom_cage_box = layout.box()
        row = custom_cage_box.row()
        row.prop(context.scene.xd_baker.attributes, "custom_cage_object", text="", placeholder="Custom Cage Object")


class XD_PT_Settings_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Settings"
    bl_category = "XD Baker"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene