import bpy
import textwrap
from bpy.app.handlers import persistent


class AddonAttribs():
    def __init__(self):
        self.info = ""

attributes = AddonAttribs()


@persistent
def addon_initialize(dummy):
    update()

@persistent
def update_when_select(scene):
    update()


class Edit_Info(bpy.types.Operator):
    bl_idname = "scene.edit_info"
    bl_label = "Edit Info"
    bl_property = "s_prop"
    bl_description = "Edit Info for current Object or Collection"

    # def __init__(self):
    #     pass

    def execute(self, context):
        active_thing = get_selected_thing()

        attributes.info = self.s_prop
        active_thing["Info"] = self.s_prop

        if self.s_prop == "":
            del active_thing["Info"]
    
    s_prop : bpy.props.StringProperty(update=execute) #type: ignore
    
    def invoke(self, context, event):
        self.s_prop = attributes.info
        width = len(attributes.info * 6) + 40
        width = max(200, min(width, 800))
        return context.window_manager.invoke_popup(self, width=width)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "s_prop", text="")


class Add_Info(bpy.types.Operator):
    bl_idname = "scene.add_info"
    bl_label = "Add Info"
    bl_property = "s_prop"
    bl_description = "Add new Info for current Object or Collection"

    # def __init__(self):
    #     pass
    
    def execute(self, context):
        active_thing = get_selected_thing()

        if self.s_prop and self.s_prop != "":
            attributes.info = self.s_prop
            active_thing["Info"] = self.s_prop
    
    s_prop : bpy.props.StringProperty(update=execute) #type: ignore
    
    def invoke(self, context, event):
        self.s_prop = attributes.info
        return context.window_manager.invoke_popup(self, width=800)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "s_prop", text="")


class INFO_PT_Panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = ""
    bl_category = "XD Info"

    # def __init__(self):
    #     pass

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Info")
        layout.label(text="|   " + get_selected_thing().name)

    def draw(self, context):
        max_lines_cnt = 20

        width = context.region.width
        chars_per_line = int(width / 8)  # Приблизительно 8 пикселей на символ
        wrapped_text = textwrap.wrap(attributes.info, width=chars_per_line)

        layout = self.layout

        if attributes.info:
            for i, line in enumerate(wrapped_text):
                if i == max_lines_cnt-1: line = line[:-3] + "..."
                if i > max_lines_cnt-1: continue

                row = layout.row(align=True)
                row.alignment = "LEFT"
                row.ui_units_y = 0.4
                row.operator("scene.edit_info", text=line, icon="NONE", emboss=False)
        else:
            layout.operator("scene.add_info", text="", icon="NONE", emboss=True)
        
        layout.separator(type="SPACE")


classes = [
    Edit_Info,
    Add_Info,
    INFO_PT_Panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.app.handlers.load_post.append(addon_initialize)
    bpy.app.handlers.depsgraph_update_post.append(update_when_select)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    if update_when_select in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(update_when_select)
    if addon_initialize in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(addon_initialize)

if __name__ == "__main__":
    register()


#########################################################
######################_FUNCTIONS_########################
#########################################################

def get_selected_thing():
    active_collection = bpy.context.collection
    active_object= bpy.context.active_object
    selected_objects = bpy.context.selected_objects

    if active_collection and not selected_objects:
        selected_thing = active_collection
    elif active_collection and selected_objects:
        selected_thing = active_object
    elif selected_objects and not active_collection:
        selected_thing = active_object
    else:
        selected_thing = None
    return selected_thing


def update():
    active_thing = get_selected_thing()
    info_attribute = active_thing.get("Info")
    if info_attribute:
        attributes.info = info_attribute
    else:
        attributes.info = ""