import bpy

from .xdpc_functions import *

class N_PT_Panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = ""
    bl_category = "XD Scatter"

    def __init__(self):
        pass

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        layout.template_list("EMITTERS_UL_Frame", "compact",
                            bpy.context.scene.xdpc_attributes, "emit_list",
                            bpy.context.scene.xdpc_attributes, "emit_idx",
                            item_dyntip_propname="XXXYYY",
                            type="DEFAULT",
                            rows=5,
                            maxrows=5,
                            sort_reverse=True,
                            sort_lock=False)
        
        # if len(bpy.context.scene.xdpc_attributes.emit_list) > 1:
        #     active_index = bpy.context.scene.xdpc_attributes.emit_idx
        # else:
        #     active_index = 0
        
        # try:
        #     bpy.context.scene.xdpc_attributes.emit_list[active_index]
        # except:
        #     return
        active_index = active_index = bpy.context.scene.xdpc_attributes.emit_idx
        active_emitter = bpy.context.scene.xdpc_attributes.emit_list[active_index]
        
        if active_emitter.type == "ADD": return
        
        props_box = layout.box()
        props_box.prop(active_emitter, "emitter_collection", text="", placeholder="Collection", expand=True)
        #print(active_emitter.inst_list[0])
        
        props_box.template_list("INSTANCES_UL_Frame", "compact",
                            active_emitter, "inst_list",
                            active_emitter, "inst_idx",
                            item_dyntip_propname="XXXYYY",
                            type="DEFAULT",
                            rows=5,
                            maxrows=5,
                            sort_reverse=True,
                            sort_lock=False)
        
        #props_box.prop(active_emitter.inst_list, "instance", text="", placeholder="Instance", expand=True)



        if active_emitter.inst_list:
            props_box.label(text="Instance: " + active_emitter.inst_list[0].name)


class EMITTERS_UL_Frame(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):       
        if item.type == "ADD":
            row = layout.row(align=True)
            row.operator('emitter.add_item', text=' ', icon='ADD', emboss=False).index = item.index # кнопка добавления айтема
            row.alignment = 'EXPAND'
        else:
            row = layout.row(align=True)
            column_left = row.split(align=True)
            row_left = column_left.row(align=True)
            row_left.alignment = 'LEFT'
            column_center = row.split(align=True)
            row_center = column_center.row(align=True)
            row_center.alignment = 'EXPAND'
            column_right = row.split(align=True)
            row_right = column_right.row(align=True)
            row_right.alignment = 'RIGHT'

            row_left.operator('emitter.rem_item', text='', icon='REMOVE', emboss=False).index = item.index # кнопка удаления айтема
            # row_center.operator('instance.rename_item', text=item.name, icon='NONE', emboss=False).index = item.index # поле указания эмиттера
            row_center.prop(item, "emitter", text="", placeholder="Emitter", emboss=False, expand=True)
            row_right.operator('emitter.item_up', text='', icon='EXPORT', emboss=False).index = item.index # кнопка перемещения айтема вверх
            row_right.prop(item, "enabled", text="", emboss=True)
            row_center.enabled = item.enabled


class INSTANCES_UL_Frame(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align=True)
        column_left = row.split(align=True)
        row_left = column_left.row(align=True)
        row_left.alignment = 'LEFT'
        column_center = row.split(align=True)
        row_center = column_center.row(align=True)
        row_center.alignment = 'EXPAND'
        column_right = row.split(align=True)
        row_right = column_right.row(align=True)
        row_right.alignment = 'RIGHT'
        
        # if item.type == "ADD":
        #     row_left.operator('instance.add_item', text='', icon='ADD', emboss=False).emitter_name = data.name # кнопка добавления айтема
        # else:
        #     row_left.operator('instance.rem_item', text='', icon='REMOVE', emboss=False).index = item.index # кнопка удаления айтема
        #     row_center.prop(item, "instance", text="", placeholder="Instance", emboss=False, expand=False)
        #     row_right.prop(item, "factor", text="", emboss=False)
        
        row_center.label(text=item.name)
        row_right.prop(item, "factor", text="", emboss=False)


class AddEmitterButton(bpy.types.Operator):
    bl_idname = "emitter.add_item"
    bl_label = "Add Emitter"
    bl_description = "Add a Emitter to the list"
    bl_options = {'REGISTER'}
    
    index: bpy.props.IntProperty() # type: ignore
    
    def execute(self, context):
        emit_list = context.scene.xdpc_attributes.emit_list
        new_emitter = emit_list.add()
        new_emitter.index = len(emit_list) - 1
        new_emitter.name = ""
        new_emitter.type = "EMITTER"
        return {'FINISHED'}

class RemEmitterButton(bpy.types.Operator):
    bl_idname = "emitter.rem_item"
    bl_label = "Remove Emitter"
    bl_description = "Remove emitter from the list"
    bl_options = {'REGISTER'}
    
    index: bpy.props.IntProperty() # type: ignore
    
    def execute(self, context):
        remove_proxy_objects(self.index)
        remove_emitter_item(self.index)
        clean_instances_of_empty_emitter() ###
        sort_emitters_indices()
        reset_active_index()
        return {'FINISHED'}


class UpEmitterButton(bpy.types.Operator):
    bl_idname = "emitter.item_up"
    bl_label = "Emitter Item Up"
    bl_description = "Change Emitters hierarchy Position"
    bl_options = {'REGISTER'}

    index: bpy.props.IntProperty() # type: ignore

    def execute(self, context):
        emit_list = context.scene.xdpc_attributes.emit_list
        current_item = emit_list[self.index]
        #print("current_item: ", current_item.name, current_item.index)
        #print(self.index)
        if self.index != len(emit_list) - 1:
            emit_list.move(self.index, self.index+1)
            #emit_list.move(self.index, len(emit_list) - 1)
        
        for idx, item in enumerate(emit_list):
            emit_list[item.name].index = idx
        
        return {'FINISHED'}


class AddInstanceButton(bpy.types.Operator):
    bl_idname = "instance.add_item"
    bl_label = "Add Instance"
    bl_description = "Add a Instance to the list"
    bl_options = {'REGISTER'}
    
    emitter_name: bpy.props.StringProperty() # type: ignore
    
    def execute(self, context):
        print("instance.add_item")
        emitter = context.scene.xdpc_attributes.emit_list[self.emitter_name]
        inst_list = emitter.inst_list
        new_inst = inst_list.add()
        new_inst.index = len(inst_list) - 1
        new_inst.name = "Instance " + str(new_inst.index)
        new_inst.type = "INSTANCE"
        new_inst.factor = 0

        #append_instance(self, context)
        
        return {'FINISHED'}


class RemInstanceButton(bpy.types.Operator):
    bl_idname = "instance.rem_item"
    bl_label = "Remove Instance"
    bl_description = "Remove a instance from the list"
    bl_options = {'REGISTER'}
    
    index: bpy.props.IntProperty() # type: ignore
    
    def execute(self, context):
        inst_list = context.scene.xdpc_attributes.emit_list[self.index].inst_list
        
        if inst_list[self.index].type == "INSTANCE":
            inst_list.remove(self.index)
            
            for idx, inst in enumerate(inst_list): # пересчитываем индексы для правильной нумерации
                inst.index = idx
                inst_list[0].enabled = True
        
        return {'FINISHED'}



panel_classes = [
    N_PT_Panel,
    EMITTERS_UL_Frame,
    INSTANCES_UL_Frame,
    AddEmitterButton,
    RemEmitterButton,
    UpEmitterButton,
    AddInstanceButton,
    RemInstanceButton
    ]