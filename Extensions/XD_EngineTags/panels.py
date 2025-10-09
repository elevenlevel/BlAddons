import bpy, os
from bpy.utils import previews
from .utilities import close_invoke_popup, clean_list, write_tags_to_object, debug_log


icons = previews.new()
path = os.path.join(os.path.dirname(__file__), "icons")
icons.load(name="checked", path=os.path.join(path,"based_checked.svg"), path_type="IMAGE")
icons.load(name="unchecked", path=os.path.join(path,"based_unchecked.svg"), path_type="IMAGE")
icons.load(name="partly_checked", path=os.path.join(path,"based_p_checked.svg"), path_type="IMAGE")


class InvokeInputTagOperator(bpy.types.Operator):
    """Открывает окно ввода тега"""
    bl_idname = "scene.invoke_input_tag"
    bl_label = "Invoke Input Tag"
    bl_description = "Invoke Input Tag"
    bl_property = "tag_name"
    bl_show_header=True

    mouse_x : bpy.props.IntProperty() # type: ignore
    mouse_y : bpy.props.IntProperty() # type: ignore

    def execute(self, context):
        bpy.ops.scene.add_user_tag(tag_name=self.tag_name)
        close_invoke_popup(self.mouse_x, self.mouse_y)
    
    tag_name : bpy.props.StringProperty(update=execute) # type: ignore

    def invoke(self, context, event):
        self.mouse_x, self.mouse_y = event.mouse_x, event.mouse_y
        return context.window_manager.invoke_popup(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "tag_name", text="", icon="NONE")


class InvokeRenameTagOperator(bpy.types.Operator):
    """Открывает окно переименования тега"""
    bl_idname = "scene.invoke_rename_tag"
    bl_label = "Invoke Rename Tag"
    bl_description = "Click to rename Tag"
    bl_property = "new_name"
    
    mouse_x : bpy.props.IntProperty() # type: ignore
    mouse_y : bpy.props.IntProperty() # type: ignore

    def execute(self, context):
        debug_log({'INFO'}, "InvokeRenameTagOperator")

        xdet_attributes = bpy.context.scene.xdet_attributes
        old_name = self.tag_name
        new_name = self.new_name.strip()

        if new_name == "":
            close_invoke_popup(self.mouse_x, self.mouse_y)
            return

        for tag in xdet_attributes.user_tags:
            if tag.name == old_name:
                tag.name = new_name
                tag.state = str(tag.state)
        
        for tag in xdet_attributes.mega_tags:
            if tag.name == old_name:
                tag.name = new_name
                tag.state = str(tag.state)

        all_objects = bpy.data.objects
        for object in all_objects:
            if object.get("Tags") is None:
                continue

            obj_tags_list = object.get("Tags").split(",")
            obj_tags_list = clean_list(obj_tags_list)

            if old_name in obj_tags_list:
                obj_tags_list.remove(old_name)
                obj_tags_list.append(new_name)
            
            obj_tags_list = list(sorted(set(obj_tags_list)))
            xdet_attributes.tags_string = ",".join(obj_tags_list)
            write_tags_to_object(object)
        
        close_invoke_popup(self.mouse_x, self.mouse_y)
    
    tag_name : bpy.props.StringProperty() # type: ignore
    new_name : bpy.props.StringProperty(update=execute) # type: ignore

    def invoke(self, context, event):
        self.mouse_x, self.mouse_y = event.mouse_x, event.mouse_y
        return context.window_manager.invoke_popup(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "new_name", text="", icon="NONE", placeholder=self.tag_name)


class ShowHideGroupOperator(bpy.types.Operator):
    """Сворачивает и разворачивает расширенные параметры аддона"""
    bl_idname = "scene.show_hide_group"
    bl_label = "Show/Hide Group"
    bl_description = "Show/Hide Group"

    def execute(self, context):
        xdet_attributes = bpy.context.scene.xdet_attributes
        xdet_attributes.show_advanced = not xdet_attributes.show_advanced
        return {'FINISHED'}


class PropertyTagIcon(bpy.types.Operator):
    """Существует исключительно для отрисовки подсказки к иконке тега из параметров аддона"""
    bl_idname = "scene.property_tag_icon"
    bl_label = "This tag"
    bl_description = "This tag from addon Properties"

    def execute(self, context):
        return {'FINISHED'}


class PrefabLinksInfo(bpy.types.Operator):
    """Кнопка предупреждения о наличии на некоторых объектах свойства PrefabLink"""
    bl_idname = "scene.prefab_links_info"
    bl_label = "Prefab Links Info"
    bl_description = "Prefab Links Info"

    my_description : bpy.props.StringProperty() # type: ignore
    @classmethod
    def description(cls, context, properties):
        tooltips_list = []
        for item in bpy.context.scene.xdet_attributes.prefab_links:
            tooltips_list.append(item.name)
        
        tooltips_str = ", ".join(tooltips_list)
        return tooltips_str

    def execute(self, context):
        debug_log(self.bl_label)
        prefab_links = bpy.context.scene.xdet_attributes.prefab_links
        
        if len(prefab_links) == 0:
            return {'FINISHED'}
        
        selected_objects = bpy.context.selected_objects
        pf_objects = []

        for object in selected_objects:
            if object.name in prefab_links:
                pf_objects.append(object)
        
        for object in selected_objects:
            object.select_set(False)
        
        for object in pf_objects:
            object.select_set(True)
        
        bpy.context.view_layer.objects.active = pf_objects[0]
        
        return {'FINISHED'}


class EngineTagsAddonPanel(bpy.types.Panel):
    """Основное окно аддона"""
    bl_label = ""
    bl_idname = "SCENE_PT_tags_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XD Engine"
    bl_description = "Assign user properties to objects for use it in Game Engine"

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        row = self.layout.row(align=True)
        row.alignment = 'LEFT'
        row.label(text="XD Tags")
        if bpy.context.scene.xdet_attributes.mega_mode:
            row.label(text="(Scene)", icon="NONE")
        else:
            sel_objs_count = len(bpy.context.selected_objects)
            row.label(text=f"({sel_objs_count} Selected)", icon="NONE")

    def _user_tags_list(self, layout, user_tags, enable): # список пользовательских тегов
        property_tags = bpy.context.scene.xdet_attributes.property_tags

        if bpy.context.scene.xdet_attributes.mega_mode:
            tags = bpy.context.scene.xdet_attributes.mega_tags
        else:
            tags = user_tags
        
        for item in tags:
            if item.name == "": continue

            row = layout.row(align=True)
            
            left_column = row.column(align=True)
            left_column.alignment = 'LEFT'
            right_column = row.column(align=True)
            right_column.alignment = 'RIGHT'
            left_row = left_column.row(align=True)
            left_row.alignment = 'CENTER'
            left_row.ui_units_y = 0.6
            right_row = right_column.row(align=True)
            right_row.alignment = 'RIGHT'
            right_row.ui_units_y = 0.6
            
            left_row.operator("scene.remove_user_tag", text="", icon="X", emboss=False).tag_name = item.name # -
            check_icon = icons['checked'].icon_id if item.state=="True" else icons['partly_checked'].icon_id if item.state=="Partly" else icons['unchecked'].icon_id
            left_row.operator("scene.update_user_tags", text="", icon_value=check_icon, emboss=False).tag_name = item.name
            left_row.operator("scene.invoke_rename_tag", text=item.name, icon="NONE", emboss=False).tag_name = item.name
            #left_row.scale_x = 0.7
            
            right_row.separator()
            column1 = right_row.column(align=True)
            column1.enabled = False
            column2 = right_row.column(align=True)
            column2.enabled = item.exists
            if bpy.context.scene.xdet_attributes.mark_property_tags:
                if item.name in property_tags:
                    column1.operator("scene.property_tag_icon", text="", icon="FILE_CACHE", emboss=False)
            column2.operator("scene.select_like_this", text="", icon="RESTRICT_SELECT_OFF", emboss=False).tag_name = item.name
    
    def _new_tag_string(self, layout, user_tags, enable): # строка для добавления нового тега
        new_tag_row = layout.row(align=True)
        new_tag_row.enabled = enable
        new_tag_row.ui_units_y = 0.6
        new_tag_row.alignment = "LEFT"
        new_tag_row.operator("scene.invoke_input_tag", text="New", icon="ADD", emboss=False) # +
    
    def _info_row(self, layout, enable): # строка для информации
        prefab_links = bpy.context.scene.xdet_attributes.prefab_links
        prefab_links_count = len(prefab_links)
        info_row = layout.row(align=True)
        info_row.ui_units_y = 0.7
        if bpy.context.scene.xdet_attributes.mega_mode:
            info_row.alert = True
            info_row.alignment = 'CENTER'
            info_row.label(text="Select and Search Objects by Tags", icon="QUESTION")
        elif prefab_links_count > 0:
            info_row.alert = True
            info_row.alignment = 'CENTER'
            info_row.operator("scene.prefab_links_info", text=f"{prefab_links_count} of selected objects is prefab link!", icon="ERROR", emboss=False)
        else:
            info_row.label(text="")
    
    def _button_line(self, layout, enable): # строка для кнопок
        btn_row = layout.row(align=True)
        btn_row.alignment = "EXPAND"
        btn_row.operator("scene.select_similar", text="Select Similar", icon="NONE")
        #btn_row.enabled = enable
        column1 = btn_row.column(align=True)
        column1.operator("scene.clear_tags", text="Clear Tags", icon="NONE")
        if bpy.context.scene.xdet_attributes.mega_mode:
            column1.enabled = False
    
    def _advanced_group(self, layout, enable):
        show_advanced = bpy.context.scene.xdet_attributes.show_advanced

        add_box = layout.box()
        arrow_row = add_box.row(align=True)
        arrow_row.scale_y = 0.5
        arrow_row.operator("scene.show_hide_group", text="Advanced", emboss=False, icon="TRIA_DOWN" if show_advanced else "TRIA_RIGHT")
        if show_advanced:
            row1 = add_box.row(align=True)
            row1.operator("scene.restore_default", text="Restore Default", icon="NONE")
            #row1.prop(bpy.context.scene.xdet_attributes, "mark_property_tags", text="Mark Property Tags", icon="NONE", toggle=True)
            row2 = add_box.row(align=True)
            column2 = row2.column(align=True)
            column2.operator("scene.clear_all_objects", text="Clear All Objects", icon="NONE").objects_only = True

    def draw(self, context):
        xdet_attributes = bpy.context.scene.xdet_attributes
        show_panels = xdet_attributes.show_panels
        user_tags = xdet_attributes.user_tags

        layout = self.layout
        list_box = layout.box()
        self._user_tags_list(list_box, user_tags, show_panels)
        self._new_tag_string(list_box, user_tags, show_panels)
        self._info_row(list_box, show_panels)
        self._button_line(layout, show_panels)
        self._advanced_group(layout, show_panels)


class PreferencesPanel(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        xdet_attributes = bpy.context.scene.xdet_attributes
        tags_row = layout.row(align=True)
        tags_row.alignment = 'EXPAND'
        tags_row.prop(xdet_attributes, "property_tags", text="Property Tags:", expand=True)
        tags_row.operator("scene.set_default_parms", text="", icon="FILE_REFRESH")