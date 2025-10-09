from ..mv_utilities import *

def __set_foo_attributes(func):
    func.name = "Zero Length Edges"
    func.foo = "check_zero_length_edges"
    func.group = "topology"
    func.report = "failed"
    func.info = "Проверка на наличие ребер с нулевой длиной"
    return func

@__set_foo_attributes
@rest_editor_state
def check_zero_length_edges(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue

        bpy.context.view_layer.objects.active = object

        bad_edges = set()

        bm = bmesh.new()
        bm.from_mesh(object.data)

        for edge in bm.edges:
            if edge.calc_length() == 0:
                bad_edges.add(edge.index)
        
        bm.free()

        if len(bad_edges) > 0:
            checked_objects[object.name] = ["EDGE", bad_edges]
            success = set_warning_type(check_type)
    
    formate_result_string(context, check_type, success, checked_objects)