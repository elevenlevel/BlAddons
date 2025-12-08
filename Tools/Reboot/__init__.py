# Add-on information
# Добавил кнопку в header окна view3d

#bl_info = {
#	"name" : "Reboot",
#	"author" : "(saidenka) meta-androcto",
#	"version" : (0,1),
#	"blender" : (2, 80, 0),
#	"location" : "File Menu",
#	"description" : "Reboot Blender without save",
#	"warning" : "",
#	"wiki_url" : "",
#	"tracker_url" : "",
#	"category" : "System"
#}

import bpy
import os, sys
import subprocess


class RestartBlender(bpy.types.Operator):
	bl_idname = "wm.restart_blender"
	bl_label = "Reboot Blender"
	bl_description = "Press to reboot Blender"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		py = os.path.join(os.path.dirname(__file__), "wm.console_toggle.py")
		filepath = bpy.data.filepath
		if (filepath != ""):
			subprocess.Popen([sys.argv[0],filepath, '-P', py])
		else:
			subprocess.Popen([sys.argv[0], '-P', py])
		bpy.ops.wm.quit_blender()
		print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-")
		return {'FINISHED'}

def menu_func(self, context):
	layout = self.layout
	layout.separator()
	layout.operator(RestartBlender.bl_idname, icon="RECOVER_LAST", text="Reboot Blender")
	layout.separator()

def header_func(self, context):
	layout = self.layout
	layout.operator(RestartBlender.bl_idname, icon="RECOVER_LAST", text="")
	layout.separator()

def register():
	bpy.utils.register_class(RestartBlender)
	bpy.types.TOPBAR_MT_file.prepend(menu_func)
	bpy.types.VIEW3D_HT_header.prepend(header_func)

def unregister():
	bpy.utils.unregister_class(RestartBlender)   
	bpy.types.TOPBAR_MT_file.remove(menu_func)
	bpy.types.VIEW3D_HT_header.remove(header_func)

if __name__ == "__main__":
	register()