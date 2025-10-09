import datetime
import math
import numpy as np
import os
import time
import bmesh

import bpy
import bpy_extras
from bpy_extras import node_shader_utils
import mathutils
import json
import struct

def get_data(obj, idx):
    i_layer = None
    p_layer = None
    r_layer = None
    s_layer = None
    n_layer = None
    c0_layer = None
    uv0_layer = None
    
    index = []
    position = []
    rotation = []
    scale = []
    normal = []
    color0 = []
    texcoord0 = []
    
    evaluated_obj = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    attributes = evaluated_obj.data.attributes
    
    try: i_layer = attributes["INDEX"]
    except: pass
    try: p_layer = attributes["POSITION"]
    except: pass
    try: r_layer = attributes["ROTATION"]
    except: pass
    try: s_layer = attributes["SCALE"]
    except: pass
    try: n_layer = attributes["NORMAL"]
    except: pass
    try: c0_layer = attributes["COLOR0"]
    except: pass
    try: uv0_layer = attributes["TEXCOORD0"]
    except: pass
    #print(obj.name, p_layer)
    pointcount = 0

    for vertex in evaluated_obj.data.vertices:
        pointcount += 1
        vertex_index = vertex.index
        index.append(idx)
        
        if i_layer != None:
            i_value = i_layer.data[vertex_index].value
            index.append(i_value)
        if p_layer != None:
            p_value = p_layer.data[vertex_index].vector
            position.append(tuple(p_value))
        if r_layer != None:
            r_value = r_layer.data[vertex_index].value
            rotation.append(tuple(r_value))
        if s_layer != None:
            s_value = s_layer.data[vertex_index].vector
            scale.append(tuple(s_value))
        if n_layer != None:
            n_value = n_layer.data[vertex_index].vector
            normal.append(tuple(n_value))
        if c0_layer != None:
            c_value = c0_layer.data[vertex_index].color
            color0.append(tuple(c_value))
        if uv0_layer != None:
            uv_value3 = uv0_layer.data[vertex_index].vector
            uv_value = mathutils.Vector((uv_value3.x, uv_value3.y))
            texcoord0.append(tuple(uv_value))
    
    return pointcount, index, position, rotation, scale, normal, color0, texcoord0

def mesh_to_dict(context):
    objs_dict = {}
    pt_count = 0
    instance_list = []
    index_list = [] # TODO: индекс нужно назначать в этом скрипте из иерархии, а не из облака точек
    position_list = []
    rotation_list = []
    scale_list = []
    normal_list = []
    color0_list = []
    texcoord0_list = []

    objects = bpy.data.collections["XD_PROXY_COLLECTION"].objects
    for idx, obj in enumerate(objects):
        if not obj.name.startswith("XD_SCATTER"): continue
        if not obj.visible_get(): continue # пропускаю скрытые объекты
        print("obj[INSTANCE]: ", obj["INSTANCE"])
        pointcount, index, position, rotation, scale, normal, color0, texcoord0 = get_data(obj, idx)
        pt_count += pointcount
        instance_list.append(obj["INSTANCE"])
        index_list.append(index)
        position_list.append(position)
        rotation_list.append(rotation)
        scale_list.append(scale)
        normal_list.append(normal)
        color0_list.append(color0)
        texcoord0_list.append(texcoord0)
    
    objs_dict["POINT_COUNT"] = pt_count
    objs_dict["INSTANCE"] = tuple(instance_list)
    objs_dict["INDEX"] = tuple(index_list)
    objs_dict["POSITION"] = tuple(position_list)
    objs_dict["ROTATION"] = tuple(rotation_list)
    objs_dict["SCALE"] = tuple(scale_list)
    objs_dict["NORMAL"] = tuple(normal_list)
    objs_dict["COLOR0"] = tuple(color0_list)
    objs_dict["TEXCOORD0"] = tuple(texcoord0_list)
    
    return objs_dict

def save_file(context, dict, filepath="", YMD=2025_03_001):
    scatter_collection = bpy.data.collections["XD_PROXY_COLLECTION"]
    
    with open(filepath[:-4]+"json", "w") as file:
        json.dump(dict, file, indent=4)
        file.close()
    
    instance_list = [obj["INSTANCE"] for obj in scatter_collection.objects if obj["INSTANCE"] != ""]
    instance_list_s = ",".join(instance_list) + "\0" # TODO: нужна ли сырая строка для \0 ?
    
    pointcount = dict["POINT_COUNT"]
    #print("pointcount: ", pointcount)
    index = [np.uint8(value) for item in dict["INDEX"] for value in item]
    position = [np.float32(coord) for sublist in dict["POSITION"] for vector in sublist for coord in vector]
    rotation = [np.float32(coord) for sublist in dict["ROTATION"] for vector in sublist for coord in vector]
    scale = [np.float16(coord) for sublist in dict["SCALE"] for vector in sublist for coord in vector]
    normal = [np.float16(coord) for sublist in dict["NORMAL"] for vector in sublist for coord in vector]
    color0 = [np.uint8(coord * 255) for sublist in dict["COLOR0"] for vector in sublist for coord in vector]
    texcoord0 = [np.float32(coord) for sublist in dict["TEXCOORD0"] for vector in sublist for coord in vector]
    
    # print(instance)
    # print(index)
    # print(position)
    # print(rotation)
    # print(scale)
    # print(normal)
    # print(color0)
    # print(texcoord0)
    
    with open(filepath, "wb") as file:
        # TODO: оформить повторяющийся код в функции
        
        # HEADER
        file.write(bytes(bytearray("XDPC", "utf-8"))) # заголовок
        
        version_pack = struct.pack("I", np.uint32(YMD))
        file.write(bytes(bytearray(version_pack)))
        
        file.write(bytes(bytearray("POINTCOUNT", "utf-8"))) # pointcount
        pointcount_pack = struct.pack("I", np.uint32(pointcount)) # pointcount
        file.write(bytes(bytearray(pointcount_pack)))

        # =====================START INSTANCES=======================
        file.write(bytes(bytearray("INSTANCES", "utf-8"))) # instances
        file.write(bytes(bytearray(instance_list_s, "utf-8"))) # instances
        # =====================FINISH INSTANCES======================
        
        # DATA
        file.write(bytes(bytearray("INDICES", "utf-8")))
        for item in index:
            index_pack = struct.pack("B", item)
            file.write(bytes(bytearray(index_pack)))
        
        file.write(bytes(bytearray("POSITION", "utf-8")))
        for item in position:
            position_pack = struct.pack("f", item)
            file.write(bytes(bytearray(position_pack)))
        
        file.write(bytes(bytearray("ROTATION", "utf-8")))
        for item in rotation:
            rotation_pack = struct.pack("f", item)
            file.write(bytes(bytearray(rotation_pack)))
        
        file.write(bytes(bytearray("SCALE", "utf-8")))
        for item in scale:
            scale_pack = struct.pack("e", item)
            file.write(bytes(bytearray(scale_pack)))
        
        file.write(bytes(bytearray("NORMAL", "utf-8")))
        for item in normal:
            normal_pack = struct.pack("e", item)
            file.write(bytes(bytearray(normal_pack)))
        
        file.write(bytes(bytearray("COLOR0", "utf-8")))
        for item in color0:
            color0_pack = struct.pack("B", item)
            file.write(bytes(bytearray(color0_pack)))
        
        file.write(bytes(bytearray("TEXCOORD0", "utf-8")))
        for item in texcoord0:
            texcoord0_pack = struct.pack("f", item)
            file.write(bytes(bytearray(texcoord0_pack)))
        
        file.close()
    
    # with open(filepath, "rb") as file:
    #     for i in range(20):
    #         header = file.read(i)
    #         print(header.decode("utf-8"))

def save_single(context, filepath=""):
    pass

def save(operator, context,
         filepath="",
         use_selection=False,
         use_visible=False,
         use_active_collection=False,
         collection="",
         batch_mode='OFF',
         use_batch_own_dir=False,
         **kwargs
         ):
    """Export Point Cloud as file"""
    start_time = time.process_time()
    
    is_file_browser = context.space_data.type == 'TOPBAR'
    
    if is_file_browser:
        dict = mesh_to_dict(context)
        save_file(context, dict, filepath=filepath)
        save_single(context)
    else:
        dict = mesh_to_dict(context)
        save_file(context, dict, filepath=filepath)
        save_single(context)
    
    print('export finished in %.4f sec.' % (time.process_time() - start_time))
    return {'FINISHED'}