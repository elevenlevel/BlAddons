# добавить очистку остатков ноды с свойством MatLayersData

import bpy
from .ls_panels import *
from .ls_utils import *


class Layers(bpy.types.PropertyGroup):
	albedo : bpy.props.StringProperty() # type: ignore
	geometry : bpy.props.StringProperty() # type: ignore
	tint: bpy.props.FloatVectorProperty(name="Tint Color", subtype='COLOR', size=4, min=0.0, max=1.0, default=(1.0, 1.0, 1.0, 1.0), description="Цвет с альфа‑каналом") # type: ignore
	exposure : bpy.props.FloatProperty() # type: ignore
	smoothnessMultiplier : bpy.props.FloatProperty() # type: ignore
	metallic : bpy.props.FloatProperty() # type: ignore


#=======ATTRIBUTES==========
old_path = ""
idx = 0
refresh = False


class NodeShaderLinks(bpy.types.PropertyGroup):
	def _replace_me(self, context):
		global idx
		global refresh
        
		if self.path == context.window_manager.temp_path or self.path == "":
			return None
		
		if refresh:
			refresh = False
		else:
			if idx == 0:
				bpy.ops.object.build_shader_op(lm_path=self.path)
			else:
				idx = 0
				return None
                
			idx += 1
            
	path : bpy.props.StringProperty(subtype='FILE_PATH', default = "", update=_replace_me, description="Path to *.MatLayers File") # type: ignore
	replace : bpy.props.BoolProperty(default=False, description="Replace Node") # type: ignore
	l_count : bpy.props.IntProperty(default=0, description="Layers count") # type: ignore
	layers : bpy.props.CollectionProperty(type=Layers)  # type: ignore


class BadTextures(bpy.types.PropertyGroup):
	texture : bpy.props.StringProperty(name="Texture Path", default="", subtype='FILE_PATH') # type: ignore
#============================


class ShowNoTextureDialog(bpy.types.Operator):
	"""
	Диалоговое окно с предупрежденем об отсутствующих текстурах
	"""
	bl_idname = "object.show_no_texture_dialog"
	bl_label = "No Texture Dialog"
	bl_description = "No Texture Dialog"
	bl_options = {'REGISTER', 'INTERNAL'}
    
	def invoke(self, context, event):
		print("Show no texture dialog")
        
		return context.window_manager.invoke_popup(self, width=300)
        
	def draw(self, context):
		layout = self.layout
		
		layout.label(text="Texture path is NOT EXIST!", icon="ERROR")
		sep = layout.separator(type='LINE')
        
		for item in context.scene.bad_textures:
			row = layout.row()
			row.label(text=str(item.texture))
	
	def execute(self, context):
		return {'FINISHED'}


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
		
		global refresh
        
		active_tree = get_active_tree()
		active_node = get_active_node(active_tree)
		
		group_parms = {}
		group_parms["name"] = active_node.name
		group_parms["label"] = active_node.label
		group_parms["use_custom_color"] = active_node.use_custom_color
		group_parms["color"] = active_node.color
		group_parms["custom_properties"] = active_node['mat_layers_data']
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
        
		refresh = True
        
		lm_path = active_node.shader_links.path
        
		remove_group_node(active_tree, active_node)
		
		matlayers_data = get_matlayers_data(lm_path)
		construct_group_node(active_tree, matlayers_data, group_parms, lm_path)
        
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
	bl_label = "Build Shader"
	bl_description = "Build Shader"
	bl_options = {'REGISTER', 'INTERNAL'}
    
	lm_path : bpy.props.StringProperty(subtype='FILE_PATH', name="Path", default="",) # type: ignore
    
	def execute(self, context):
		print("Build Shader")
		
		active_tree = get_active_tree()
		active_node = active_tree.nodes.active
        
		# получаем данные из *.MatLayers файла
		matlayers_data = get_matlayers_data(self.lm_path) # содержимое файла *.MatLayers
        
		if matlayers_data is None:
			print(f"matlayers_data is None!")
			return {'CANCELLED'}
		
		# получаем активный материал
		material = get_active_material() # активный материал
		if not material:
			return {'CANCELLED'}
		material["MatLayers_data"] = matlayers_data
		
		# проверяем наличие указанных текстур
		existing = check_existing_textures(self.lm_path)
		
		if not existing:
			context.window_manager.temp_path = ""
			context.scene.bad_textures.clear()
			return {'CANCELLED'}
        
		# начинаем построение дерева нод
		remove_all_trash()
		add_node(group_name="Mat Layers", node_parms=None, lm_path=self.lm_path)
        
		return {'FINISHED'}


classes = (
	Layers,
	NodeShaderLinks,
	BadTextures,
	ShowNoTextureDialog,
	AskToReplaceNode,
	ShaderEditorPanel,
	BuildShader_OP
	)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	
	if not hasattr(bpy.types.Node, "shader_links"):
		bpy.types.Node.shader_links = bpy.props.PointerProperty(type=NodeShaderLinks)
	if not hasattr(bpy.types.Scene, "bad_textures"):
		bpy.types.Scene.bad_textures = bpy.props.CollectionProperty(type=BadTextures)
    
	def _upd(self, context):
		global old_path
		
		if self.temp_path != old_path and self.temp_path != "":
			bpy.ops.object.build_shader_op(lm_path = self.temp_path)
		# self.temp_path = ""
        
		old_path = self.temp_path
    
	if not hasattr(bpy.types.WindowManager, 'temp_path'):
		# Создаем временный путь 
		bpy.types.WindowManager.temp_path = bpy.props.StringProperty(
			subtype='FILE_PATH',
			name="Temp Path",
			default="",
			update=_upd
		)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	
	del bpy.types.Scene.bad_textures
	del bpy.types.Node.shader_links


if __name__ == "__main__":
	register()