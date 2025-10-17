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

import dither

import bpy
import numpy as np
#from . dither import floyd_steinberg

from .sdf_module import distance_transform_edt

#@numba.jit("f4[:,:,:](f4[:,:,:])", nopython=True, nogil=True)
# @numba.jit(nopython=True)
# def floyd_steinberg(image, shagreen):
#     # алгоритм дизеринга
#     Lx, Ly, Lc = image.shape
#     for j in range(Ly):
#         for i in range(Lx):
#             for c in range(Lc):
#                 rounded = round(image[i, j, c] * shagreen) / shagreen
#                 quant_error = image[i, j, c] - rounded
#                 image[i, j, c] = rounded
#                 sixteen = 16
#                 if i < Lx - 1:
#                     image[i + 1, j, c] += quant_error * 7 / sixteen
#                 if i > 0 and j < Ly - 1:
#                     image[i - 1, j + 1, c] += quant_error * 3 / sixteen
#                 if j < Ly - 1:
#                     image[i, j + 1, c] += quant_error * 5 / sixteen
#                 if i < Lx - 1 and j < Ly - 1:
#                     image[i + 1, j + 1, c] += quant_error * 1 / sixteen
#     return image

# def floyd_steinberg(image, levels):
#     image = image.astype(np.float32)
#     height, width, channels = image.shape
#     for y in range(height):
#         for x in range(width):
#             for c in range(channels):
#                 old_pixel = image[y, x, c]
#                 new_pixel = np.round(old_pixel * levels) / levels
#                 quant_error = old_pixel - new_pixel
#                 image[y, x, c] = new_pixel
#                 if x < width - 1:
#                     image[y, x+1, c] += quant_error * 7 / 16
#                 if x > 0 and y < height - 1:
#                     image[y+1, x-1, c] += quant_error * 3 / 16
#                 if y < height - 1:
#                     image[y+1, x, c] += quant_error * 5 / 16
#                 if x < width - 1 and y < height - 1:
#                     image[y+1, x+1, c] += quant_error / 16
#     return np.clip(image, 0, 1)

def filter_dithering(context, image_data, accuracy):
    image_data_copy = image_data.copy()
    #image_data_copy = floyd_steinberg(image_data_copy, accuracy)
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