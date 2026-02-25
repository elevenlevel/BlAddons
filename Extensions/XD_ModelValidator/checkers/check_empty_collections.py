from ..mv_utilities import *

# Единый источник истины
MODULE_NAME = "Empty Collections"
MODULE_FOO = "check_empty_collections"
MODULE_GROUP = "general"
MODULE_REPORT = "warning"
MODULE_INFO = "Если в коллекции нет объектов"

def __set_foo_attributes(func):
    func.name = MODULE_NAME
    func.foo = MODULE_FOO
    func.group = MODULE_GROUP
    func.report = MODULE_REPORT
    func.info = MODULE_INFO
    return func

@__set_foo_attributes
@rest_editor_state
def check_empty_collections(context, check_type, success = "[SUCCESS]"):
    checked_objects = {} # [object.name: [bad_faces[], "Faces"]]

    for collection in select_check_entities("collections"):
        if len(collection.all_objects) == 0:
            success = set_warning_type(check_type)
            checked_objects[collection.name] = ["COLL"]

    formate_result_string(context, check_type, success, checked_objects)