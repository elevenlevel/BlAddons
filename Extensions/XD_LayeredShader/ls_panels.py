import bpy
import json

class ShaderEditorPanel(bpy.types.Panel):
	'''Основное окно аддона'''
	bl_idname = "OBJECT_PT_layered_shader"
	bl_label = "Layered Shader"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Layered Shader"
	bl_description = "Part of the addon with basic controls"
	#bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		buttons_row = layout.row(align=True)
		buttons_row.alignment = 'CENTER'
		buttons_row.operator("object.invert_checkboxes", text="Invert", icon="NONE")