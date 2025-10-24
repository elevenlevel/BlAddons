    # импорт локального модуля numba
import sys, os, importlib
current_script_path = os.path.dirname(os.path.abspath(__file__))
py_modules_path = os.path.join(current_script_path, 'py_modules')
sys.path.append(py_modules_path)

# dither_path = os.path.join(current_script_path, "dither" + "*.pyd")
# module_path = dither_path[0]  # берем первый найденный файл
# spec = importlib.util.spec_from_file_location(dither_path, module_path)
# module = importlib.util.module_from_spec(spec)
#spec.loader.exec_module(module)
# sys.modules["floyd_steinberg"] = module
# print("module_path: ", module_path)

import bpy
import numpy as np

import ctypes
from numpy.ctypeslib import as_array
import traceback
# lib_path = os.path.join(current_script_path, 'floyd_steinberg.dll')
# lib = ctypes.CDLL(lib_path)
#lib.floyd_steinberg.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
#lib.floyd_steinberg.restype = None
#lib.floyd_steinberg.restype = ctypes.c_char

def floyd_steinberg_c(image, shagreen):
    image = np.ascontiguousarray(image, dtype=np.float64)
    Lx, Ly, Lc = image.shape
    ptr = image.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    lib_path = os.path.join(current_script_path, 'floyd_steinberg.dll')
    # Проверяем существование файла
    if not os.path.exists(lib_path):
        print(f"DLL not found: {lib_path}")
    
    # Загружаем библиотеку
    try:
        lib = ctypes.CDLL(lib_path)
    except OSError as e:
        print(f"Error loading DLL: {e}")
    
    # lib.floyd_steinberg.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    # Устанавливаем типы аргументов и возвращаемого значения
    lib.floyd_steinberg.argtypes = [
        ctypes.POINTER(ctypes.c_double), 
        ctypes.c_int, 
        ctypes.c_int, 
        ctypes.c_int, 
        ctypes.c_float
    ]
    lib.floyd_steinberg.restype = None

    if not isinstance(image, np.ndarray):
        print("image должен быть numpy массивом")
    if len(image.shape) != 3:
        print("image должен быть трехмерным массивом")
    Lx, Ly, Lc = image.shape
    if Lx <= 0 or Ly <= 0 or Lc <= 0:
        print("Размеры изображения должны быть положительными")
    if not isinstance(shagreen, float) or shagreen <= 0.0:
        print("shagreen должен быть положительным числом")

    if True==False:
        print(f"Размеры изображения: {Lx}x{Ly}x{Lc}")
        print(f"Тип данных: {image.dtype}")
        print(f"Указатель на данные: {ptr}")
        print(f"Путь к DLL: {lib_path}")

    try:
        lib.floyd_steinberg(ptr, Lx, Ly, Lc, shagreen)
    except Exception as e:
        print(f"Ошибка при вызове функции: {e}")
        traceback.print_exc()

    # lib.get_message.restype = ctypes.c_char_p
    # msg = lib.get_message(b"Hello, World!")
    # print(msg.decode('utf-8'))


    return image

from .sdf_module import distance_transform_edt

def filter_dithering(context, image_data, accuracy):
    image_data_copy = image_data.copy()
    image_data_copy = floyd_steinberg_c(image_data_copy, accuracy)
    return image_data_copy

def signed_distance_transform(context, image, sdf_type):
    # расчет distance field
    sdf_shrinked = distance_transform_edt(image)
    sdf_expanded = distance_transform_edt(1 - image)

    sdf_shrinked_max = sdf_shrinked.max()
    sdf_expanded_max = sdf_expanded.max()

    sdf_shrinked = (sdf_shrinked / sdf_shrinked_max) # от 0 до 1
    sdf_expanded = (sdf_expanded / sdf_expanded_max) # от 0 до 1
    
    if sdf_type == "SDF Shrinked" and sdf_shrinked_max > 0:
        sdf = sdf_shrinked
    elif sdf_type == "SDF Expanded" and sdf_expanded_max > 0:
        sdf = sdf_expanded
    elif sdf_type == "SDF Mixed":
        #sdf = np.maximum(1-sdf_shrinked, sdf_expanded)
        sdf = ((sdf_shrinked - sdf_expanded) * 0.5 + 0.5)
    else:
        sdf = image
    return sdf

def set_rgb_from_alpha(context, sdf_type): # загружаем изображение
    bake_texture_name = context.scene.xd_baker.attributes.bake_texture_name
    image_name = bake_texture_name + "_opacity"
    image = bpy.data.images[image_name]
    
    # конвертируем изображение в массив
    width, height = image.size
    pixel_array = np.array(image.pixels[:]).reshape((height, width, 4))

    # достаем альфу
    alpha_ch = pixel_array[:, :, 3]
    
    if sdf_type != "None": # считаем sdf
        result = signed_distance_transform(context, alpha_ch, sdf_type)
    else:
        result = alpha_ch
    
    # помещаем sdf в R, G, B
    pixel_array[:, :, 0] = result
    pixel_array[:, :, 1] = result
    pixel_array[:, :, 2] = result
    pixel_array[:, :, 3] = 1.0

    image.pixels = pixel_array.flatten()