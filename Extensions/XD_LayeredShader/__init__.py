import bpy
from ls_panels import *
from ls_utils import *
from bpy.app.handlers import persistent


#=======ATTRIBUTES==========
class Links(bpy.types.PropertyGroup):
	@classmethod
	def _collect_me(cls, self, context): # метод выполнится при изменении state
		my_foo("Hello World!")
	
	name : bpy.props.StringProperty(name="Name") # type: ignore
	state : bpy.props.BoolProperty(default=False, update=Links._collect_me, name="Select Check") # type: ignore


@persistent 
def InitAddon(scene):
	'''Первоначальная настройка аддона'''
	print("Initialize addon")


class MyOperator(bpy.types.Operator):
	'''Оператор'''
	bl_idname = "object.my_operator"
	bl_label = "My Operator"
	bl_description = "My Operator"
	bl_options = {'REGISTER', 'INTERNAL'}

	def execute(self, context):
		print("Execute My Operator")
		return {'FINISHED'}


classes = (
	Links,
	ShaderEditorPanel,
	MyOperator
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	
	bpy.app.handlers.load_post.append(InitAddon)
	
	if not hasattr(bpy.types.Scene, "my_links"):
		bpy.types.Scene.my_links = bpy.props.PointerProperty(type=Links)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	
	del bpy.types.Scene.my_links

	if InitAddon in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.remove(InitAddon)

if __name__ == "__main__":
	register()