from ..mv_utilities import *

def __set_foo_attributes(func):
    func.name = "Empty Collections"
    func.foo = "check_empty_collections"
    func.group = "general"
    func.report = "warning"
    func.info = "Если в коллекции нет объектов"
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