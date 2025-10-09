import bpy


class TroubledLinksOperator(bpy.types.Operator):
    # Выделение проблемных объектов
    bl_idname = "scene.troubled_links_operator"
    bl_label = "Troubled Links Operator"
    bl_description = "Troubled Links Operator"
    
    @classmethod
    def description(cls, context, properties):
        troubled_list = list(x.name for x in bpy.context.scene.xdpl_attributes.troubled_objects)
        return "\n".join(troubled_list)
        
    def execute(self, context):
        troubled_objects = bpy.context.scene.xdpl_attributes.troubled_objects
        if len(troubled_objects) == 0:
            return {'FINISHED'}
            
        for object in bpy.data.objects:
            object.select_set(False)
        for object in troubled_objects:
            bpy.data.objects[object.name].select_set(True)
            
        bpy.context.view_layer.objects.active = bpy.data.objects[troubled_objects[0].name]
        return {'FINISHED'}


class EnginePrefabLinkAddonPanel(bpy.types.Panel):
    '''Основное окно аддона'''
    bl_label = ""
    bl_idname = "SCENE_PT_prefab_link_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XD Engine"
    bl_description = "Assign PrefabLink property to objects for use it in Game Engine"
    
    @classmethod
    def poll(cls, context):
        return True
        
    def draw_header(self, context):
        row = self.layout.row(align=True)
        row.alignment = 'LEFT'
        row.label(text="XD PrefabLink")
        
    def draw(self, context):
        xdpl_attributes = bpy.context.scene.xdpl_attributes
        layout = self.layout
        
        string_row = layout.row(align=True)
        string_row.alignment = 'EXPAND'
        string_row.enabled = bpy.context.scene.xdpl_attributes.enable_layout
        column_left = string_row.column(align=True)
        column_right = string_row.column(align=True)
        
        # строка с линком
        if not bpy.context.scene.xdpl_attributes.search_mode:
            column_left.prop(xdpl_attributes, "prefab_link", text="", placeholder="Link to Prefab")
        else:
            column_left.prop(xdpl_attributes, "search_link", text="", placeholder="Search Link", icon="VIEWZOOM")
            
        # кнопка выделения объектов по линку
        column_right.enabled = bpy.context.scene.xdpl_attributes.enable_seach_button
        column_right.operator("scene.select_linked_objects", text="", icon='VIEWZOOM')
        
        is_troubled = bpy.context.scene.xdpl_attributes.is_troubled
        
        # информационная строка
        info_row = layout.row(align=True)
        if is_troubled:
            info_row.alignment = 'EXPAND'
            info_row.alert = True
            info_row.operator("scene.troubled_links_operator", text=is_troubled, icon='ERROR', emboss=False)