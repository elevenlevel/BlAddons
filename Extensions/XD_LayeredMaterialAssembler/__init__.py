# TODO: если текстура по пути не сущестствует, то показывать диалоговое окно (продолжить/отмена)
# TODO: заполнить main_group_node['mat_layers'] содержимым файла
# TODO: 

import bpy
from .ls_panels import *
from .ls_utils import *
from bpy.app.handlers import persistent
import subprocess
import os
import json


class Layers(bpy.types.PropertyGroup):
	albedo : bpy.props.StringProperty() # type: ignore
	geometry : bpy.props.StringProperty() # type: ignore
	tint: bpy.props.FloatVectorProperty(name="Tint Color", subtype='COLOR', size=4, min=0.0, max=1.0, default=(1.0, 1.0, 1.0, 1.0), description="Цвет с альфа‑каналом") # type: ignore
	exposure : bpy.props.FloatProperty() # type: ignore
	smoothnessMultiplier : bpy.props.FloatProperty() # type: ignore
	metallic : bpy.props.FloatProperty() # type: ignore


#=======ATTRIBUTES==========
class ShaderLinks(bpy.types.PropertyGroup):
	def _collect_me(self, context):
		bpy.ops.object.build_shader_op()
	
	# node_name : bpy.props.StringProperty(name="Name") # type: ignore
	path : bpy.props.StringProperty(subtype='FILE_PATH', default = "", update=_collect_me, description="Path to *.MatLayers File") # type: ignore
	replace : bpy.props.BoolProperty(default=False, description="Replace Node") # type: ignore
	l_count : bpy.props.IntProperty(default=0, description="Layers count") # type: ignore
	layers : bpy.props.CollectionProperty(type=Layers)  # type: ignore
	h_map_path : bpy.props.StringProperty(subtype='FILE_PATH', default = "", description="Path to Height Map") # type: ignore


# если не понадобится, то удалить
@persistent 
def InitAddon(scene):
	'''Первоначальная настройка аддона'''
	# print("Initialize addon")
	pass

@persistent 
def update_addon(scene):
	# print("update_addon")
	pass

class AskToReplaceNode(bpy.types.Operator):
	"""
	Диалоговое окно с запросом на ребилд материала
	"""
	bl_idname = "object.ask_to_replace_node"
	bl_label = "Replace Node?"
	bl_description = "Replace Node"
	bl_options = {'REGISTER', 'INTERNAL'}
	
	def execute(self, context):
		"""
		Выполнение после нажатия OK
		"""
		
		active_tree = get_active_tree()
		active_node = get_active_node(active_tree)
		
		group_parms = {}
		group_parms["name"] = active_node.name
		group_parms["label"] = active_node.label
		group_parms["use_custom_color"] = active_node.use_custom_color
		group_parms["color"] = active_node.color
		group_parms["custom_properties"] = active_node['mat_layers']
		group_parms["location"] = active_node.location
		group_parms["width"] = active_node.width
		group_parms["input_links"] = {}
		group_parms["output_links"] = {}

		for input in active_node.inputs:
			if input.links:
				for link in input.links:
					group_parms["input_links"][input.name] = link.from_socket
		
		for output in active_node.outputs:
			if output.links:
				for link in output.links:
					group_parms["output_links"][output.name] = link.to_socket
		
			# group_parms["input_links"] = active_tree.links # выяснить какие линки куда подключены
			# group_parms["output_links"] = []

		remove_group_node(active_tree, active_node)
		update_addon(context.scene)
		# refresh_group_node(active_tree, group_parms)
		# add_node(group_name=group_parms.name, node_parms=group_parms)
		construct_group_node(active_tree, group_parms)
		update_addon(context.scene)
		group_parms.clear()
		return {'FINISHED'}
	
	def invoke(self, context, event):
		print("ask_to_replace_node")
		return context.window_manager.invoke_confirm(self, event=event, icon="QUESTION", confirm_text="Apply", title="Refresh Selected Node?", message="Confirm to Refresh Node!")
	
	def draw(self, context):
		layout = self.layout
		layout.label(text="Confirm to Rebuild Material?", icon="QUESTION")

class BuildShader_OP(bpy.types.Operator):
	'''
	Пересчет шейдера при замене MatLayers файла или вручную
	'''
	bl_idname = "object.build_shader_op"
	bl_label = "Rebuild Shader"
	bl_description = "Rebuild Shader"
	bl_options = {'REGISTER', 'INTERNAL'}

	def execute(self, context):
		print("Rebuild Shader")
		
		# получаем данные из *.MatLayers файла
		matlayers_data = get_matlayers_data() # содержимое файла *.MatLayers
		if matlayers_data is None:
			print(f"matlayers_data is None!")
			return {'CANCELLED'}
		
		# получаем активный материал
		material = get_active_material() # активный материал
		# materials = get_object_materials() # материалы активного объекта

		if material:
			material["MatLayers_path"] = get_matlayers_path()
			material["MatLayers_data"] = matlayers_data
		
		mat_layers = material.get('MatLayers_data')
		# print(f"matlayers_data: {matlayers_data}")

		# ЗДЕСЬ НУЖНО ЗАПОЛНИТЬ bpy.context.scene.shader_links.layers из mat_layers
		
		# layers = bpy.context.scene.shader_links.layers
		layers = bpy.types.Node.shader_links.layers
		
		for layer in mat_layers['layers']:
			current_path = bpy.context.scene.shader_links.path
			albedo_rel = layer['albedo']
			albedo_abs = os.path.abspath(os.path.join(current_path, albedo_rel))
			geometry_rel = layer['geometry']
			geometry_abs = os.path.abspath(os.path.join(current_path, geometry_rel))

			new_layer = layers.add()

			new_layer.albedo = albedo_abs
			new_layer.geometry = geometry_abs
			new_layer.tint = layer['tint']['r'], layer['tint']['g'], layer['tint']['b'], layer['tint']['a']
			new_layer.exposure = layer['exposure']
			new_layer.smoothnessMultiplier = layer['smoothnessMultiplier']
			new_layer.metallic = layer['metallic']
		
		# bpy.ops.object.ask_to_replace_node('INVOKE_DEFAULT')
		# bpy.ops.object.ask_to_replace_node('INVOKE_DEFAULT')

		add_node(group_name="Mat Layers", node_parms=None)
		update_addon(context.scene)
		return {'FINISHED'}


classes = (
	Layers,
	ShaderLinks,
	AskToReplaceNode,
	ShaderEditorPanel,
	BuildShader_OP
	)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	
	bpy.app.handlers.load_post.append(InitAddon)
	bpy.app.handlers.depsgraph_update_post.append(update_addon)
	
	if not hasattr(bpy.types.Scene, "shader_links"):
		bpy.types.Scene.shader_links = bpy.props.PointerProperty(type=ShaderLinks)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	
	bpy.app.handlers.depsgraph_update_post.remove(update_addon)
	del bpy.types.Scene.shader_links

	if InitAddon in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.remove(InitAddon)

if __name__ == "__main__":
	register()