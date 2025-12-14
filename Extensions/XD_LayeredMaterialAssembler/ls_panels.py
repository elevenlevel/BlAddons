import bpy
import json

class ShaderEditorPanel(bpy.types.Panel):
	'''Основное окно аддона'''
	bl_idname = "OBJECT_PT_layered_shader"
	bl_label = "Layered Shader"
	bl_space_type = 'NODE_EDITOR'
	bl_region_type = 'UI'
	bl_category = "Layered Shader"
	bl_description = "Part of the addon with basic controls"
	#bl_options = {'DEFAULT_CLOSED'}
    
	@classmethod
	def poll(cls, context):
		return True
    
	def execute(self, context):
		scene = bpy.context.scene
		pass
    
	def draw(self, context):
		scene = bpy.context.scene
		layout = self.layout
		buttons_row = layout.row(align=True)

		# проверяем валидность активного объекта
		active_obj = bpy.context.active_object
		# if not active_obj or active_obj.type != 'MESH':
		
		space = bpy.context.space_data
		if space.type == 'NODE_EDITOR' and space.tree_type == 'ShaderNodeTree' and space.node_tree is not None:
			buttons_row.enabled = True
		else:
			buttons_row.enabled = False
		
		buttons_row.alignment = 'EXPAND'
		buttons_row.prop(scene.shader_links, "path", text="")
		buttons_row.operator("object.rebuild_shader_op", text="", icon="FILE_REFRESH")