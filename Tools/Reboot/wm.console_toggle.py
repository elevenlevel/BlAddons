import bpy

try:
    bpy.ops.wm.console_toggle_on_top(open_console=True) # this is from another free addon, here: https://github.com/1C0D/Toggle-Console-on-Top-WindowsOnly--Blender
except AttributeError:
    bpy.ops.wm.console_toggle()