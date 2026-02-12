import bpy

class XD_PT_Panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Objects"
    bl_category = "TEST"
    
    @classmethod
    def poll(cls, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        
        layout.label(text="Hello World!")

def register():
    bpy.utils.register_class(XD_PT_Panel)


def unregister():
    bpy.utils.unregister_class(XD_PT_Panel)

if __name__ == "__main__":
    register()
