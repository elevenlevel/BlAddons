import bpy
import json

from . ls_utils import get_active_tree, get_active_node, def_mat_layers_node

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
		pass

	def draw(self, context):
		layout = self.layout
		buttons_row = layout.row(align=True)
		
		# проверяем валидность активного объекта
		is_mat_layers_node = def_mat_layers_node() # ВОТ ЭТО НАДО ОПТИМИЗИРОВАТЬ ОТСЮДА
		active_node = get_active_node(get_active_tree())
		
		# bpy.context.scene.shader_links = shader_links
		
		space = bpy.context.space_data
		if space.type == 'NODE_EDITOR' and space.tree_type == 'ShaderNodeTree' and space.node_tree is not None:
			buttons_row.enabled = True
		else:
			buttons_row.enabled = False
		
		buttons_row.alignment = 'EXPAND'
		
		#==========r
		if is_mat_layers_node:
			# Двусторонняя синхронизация
			# if wm.temp_path != active_node.shader_links.path:
			# 	wm.temp_path = active_node.shader_links.path
			
			# Показываем prop который обновляет оба значения
			buttons_row.prop(active_node.shader_links, "path", text="")
			
			# Обновляем temp при изменении
			# if active_node.shader_links.path != wm.temp_path:
			# 	wm.temp_path = active_node.shader_links.path
		else:
			# Показываем временное значение (пустое или последнее)
			buttons_row.prop(context.window_manager, "temp_path", text="", placeholder="path to MatLayers file")
		#============

		if is_mat_layers_node:
			cell = buttons_row.column(align=False)
			cell.operator("object.ask_to_replace_node", text="", icon="FILE_REFRESH") # кнопка обновления
			cell.enabled = True
		else:
			cell = buttons_row.column(align=False)
			cell.operator("object.ask_to_replace_node", text="", icon="FILE_REFRESH") # кнопка обновления
			cell.enabled = False