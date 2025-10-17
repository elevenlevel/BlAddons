import bpy
import subprocess
import os
from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy
import sys

def compile_cython_module(module_name="dither", file="dither.pyx"):
    ext_modules = [
        Extension(
            module_name,                      # Имя модуля
            [file],                # Исходный файл
            include_dirs=[numpy.get_include()]
        )
    ]

    setup(
        name='dither_module',
        ext_modules=cythonize(ext_modules),
        script_args=['build_ext', '--inplace']
    )

class INFO_PT_Panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = ""
    bl_category = "XD CythonBuilder"

    def draw(self, context):
        layout = self.layout
        layout.operator("scene.build_pyx", text="Build *.pyx", icon="RECORD_ON", emboss=True)


class BuildPYX(bpy.types.Operator):
    bl_idname = "scene.build_pyx"
    bl_label = "Build *.pyx"
    bl_description = "Build *.pyx"

    def execute(self, context):
        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path)
        file_path = os.path.join(current_dir, "dither.pyx")
        # setup_py_path = os.path.join(current_dir, "setup.py")

        # result = subprocess.run(["python", "setup.py", "build_ext", "--inplace", "-v"], cwd=current_dir, capture_output=True, text=True)
        # print(result.stdout)

        compile_cython_module(module_name="dither", file=file_path)
        return {"FINISHED"}


classes = [
    INFO_PT_Panel,
    BuildPYX
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
