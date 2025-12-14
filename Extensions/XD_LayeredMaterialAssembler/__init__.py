import bpy
from .ls_panels import *
from .ls_utils import *
from bpy.app.handlers import persistent
import subprocess
import os
import json

class Layers(bpy.types.PropertyGroup):
	diffuse : bpy.props.StringProperty() # type: ignore
	geometry : bpy.props.StringProperty() # type: ignore
	tint: bpy.props.FloatVectorProperty(name="Tint Color", subtype='COLOR', size=4, min=0.0, max=1.0, default=(1.0, 1.0, 1.0, 1.0), description="Цвет с альфа‑каналом") # type: ignore
	exposure : bpy.props.FloatProperty() # type: ignore
	smoothnessMultiplier : bpy.props.FloatProperty() # type: ignore
	metallic : bpy.props.FloatProperty() # type: ignore


#=======ATTRIBUTES==========
class ShaderLinks(bpy.types.PropertyGroup):
	def _collect_me(self, context):
		bpy.ops.object.rebuild_shader_op()
	
	# name : bpy.props.StringProperty(name="Name") # type: ignore
	path : bpy.props.StringProperty(subtype='FILE_PATH', default = "", update=_collect_me, description="Path to *.MatLayers File") # type: ignore
	replace : bpy.props.BoolProperty(default=False, description="Replace Node") # type: ignore
	l_count : bpy.props.IntProperty(default=0, description="Layers count") # type: ignore
	layers : bpy.props.CollectionProperty(type=Layers)  # type: ignore
	h_map_path : bpy.props.StringProperty(subtype='FILE_PATH', default = "", description="Path to Height Map") # type: ignore


# если не понадобится, то удалить
@persistent 
def InitAddon(scene):
	'''Первоначальная настройка аддона'''
	print("Initialize addon")


@persistent 
def update_addon(scene):
	print("update_addon")

class AskToReplaceNode(bpy.types.Operator):
	'''Диалоговое окно с запросом на ребилд материала'''
	bl_idname = "object.ask_to_replace_node"
	bl_label = "Replace Node?"
	bl_description = "Replace Node"
	bl_options = {'REGISTER', 'INTERNAL'}

	target_tree = bpy.props.PointerProperty(type=bpy.types.ShaderNodeTree) # type: ignore

	def execute(self, context):
		"""Выполнение после нажатия OK"""
		target_tree = self.target_tree
		remove_group_node(target_tree)
		create_group_node(target_tree, group_name="XXX")
		return {'FINISHED'}
	
	def invoke(self, context, event):
		print("ask_to_replace_node")
		return context.window_manager.invoke_confirm(self, event=event, icon="WARNING", confirm_text="Apply", title="Rebuild Material?", message="Confirm to Rebuild Material!")
	
	def draw(self, context):
		layout = self.layout
		layout.label(text="Confirm to Rebuild Material?", icon="QUESTION")

class RebuildShader_OP(bpy.types.Operator):
	'''Пересчет шейдера при замене MatLayers файла или вручную'''
	bl_idname = "object.rebuild_shader_op"
	bl_label = "Rebuild Shader"
	bl_description = "Rebuild Shader"
	bl_options = {'REGISTER', 'INTERNAL'}

	def execute(self, context):
		print("Rebuild Shader")
		
		# получаем данные из *.MatLayers файла
		matlayers_data = get_matlayers_data() # содержимое файла *.MatLayers
		if matlayers_data is None:
			return {'CANCELLED'}
		
		# получаем активный материал
		material = get_active_material() # активный материал
		# materials = get_object_materials() # материалы активного объекта

		if material:
			material["MatLayers_path"] = get_matlayers_path()
			material["MatLayers_data"] = matlayers_data
		
		mat_layers = material.get('MatLayers_data')

		# for layer in mat_layers['layers']:
		# 	albedo = layer['albedo']
		# 	geometry = layer['geometry']
		# 	tint = layer['tint']
		# 	exposure = layer['exposure']
		# 	smoothnessMultiplier = layer['smoothnessMultiplier']
		# 	metallic = layer['metallic']

		# bpy.ops.object.ask_to_replace_node('INVOKE_DEFAULT')

		build_mat_graph()

		return {'FINISHED'}


classes = (
	Layers,
	ShaderLinks,
	AskToReplaceNode,
	ShaderEditorPanel,
	RebuildShader_OP
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