# Аддон с различными мелкими инструментами, помогающимив разработке

# TODO: выбор объектов с непримененными трансформациями (всеми или раздельно)
# TODO: перемещение пивота в центр объекта (в центр выделенного полигона учитывая нормаль)
# TODO: выбор объектов по части имени
# TODO: 
# TODO: 

import bpy

# Функция для удаления пункта экспорта FBX из меню
def remove_fbx_export_menu(self, context):
    # Проверяем и удаляем стандартный оператор FBX
    
    self.layout.remove(self.layout.operator("export_scene.fbx", text="FBX", icon='EXPORT'))

# Регистрация класса
def register():
    bpy.types.TOPBAR_MT_file_export.append(remove_fbx_export_menu)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(remove_fbx_export_menu)

if __name__ == "__main__":
    register()