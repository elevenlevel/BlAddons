from ..mv_utilities import *

MODULE_NAME = "Sharp Edges"
MODULE_FOO = "check_sharp_edges"
MODULE_GROUP = "topology"
MODULE_REPORT = "warning"
MODULE_INFO = "Проверка на ребра с жесткими нормалями"

def __set_foo_attributes(func):
    func.name = MODULE_NAME
    func.foo = MODULE_FOO
    func.group = MODULE_GROUP
    func.report = MODULE_REPORT
    func.info = MODULE_INFO
    return func

@__set_foo_attributes
@rest_editor_state
def check_sharp_edges(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for object in select_check_entities("objects"):
        if object.type != "MESH":
            continue

        bpy.context.view_layer.objects.active = object

        bad_edges = set()

        for edge in object.data.edges:
            if edge.use_edge_sharp:
                bad_edges.add(edge.index)

        if len(bad_edges) > 0:
            checked_objects[object.name] = ["EDGE", bad_edges]
            success = set_warning_type(check_type)
    
    formate_result_string(context, check_type, success, checked_objects)
