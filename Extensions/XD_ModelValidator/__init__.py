# АДДОН ДЛЯ ПРОВЕДЕНИЯ РАЗЛИЧНЫХ МЕЛКИХ ТЕСТОВ
#TODO: состояние чекеров должно сохраняться в сцене Done
#TODO: нужен функционал выделения коллекции Done
#TODO: реализовать проверку инвертированных полигонов Done
#TODO: прописать описания для элементов интерфейса Done
#TODO: состояние чекеров должно сохраняться в сцене Done
#TODO: когда заголовок свернут, частичное отображение чекеров должно отображатьтся в значке Done
#TODO: укоротить └── в списке объектов Done
#TODO: добавить значки типа объекта перед каждым объектом Done
#TODO: сделать готовые проверки схлопывающимися Done
#TODO: progress bar https://blender.stackexchange.com/questions/3219/how-to-show-to-the-user-a-progression-in-a-script
#TODO: подсчет количества объектов в конце не правильный Done
#TODO: цветовые маркеры проверок должны сбрасываться сначала на серый при сканировании Done
#TODO: использовать значения warning и error по умолчанию из словаря Done
#TODO: Операторы BMesh https://docs.blender.org/api/current/bmesh.ops.html
#TODO: сделать пересканирование имен чекбоксов при каждом запуске Done
#TODO: сделать progress bar Done
#TODO: в репорте перенести стрелочки скрытия влево Done
#TODO: сохранять состояния скрытия групп в репорте Done
#TODO: проверять только активную группу и ее содержимое Done
#TODO: переделать Cyrillic Letters на Non Latinic Letters Done
#TODO: убрать кнопку uncheck all и реализовать (un)Check All Done
#TODO: extra symbols проверяет лишнее Done
#TODO: длинные имена объектов в репорте странно выравниваются Canc
#TODO: добавить индивидуальные подсказки для каждого чекера Done
#TODO: снова неправильный подсчет проверенных объектов и коллекций. Взять из select_check_entities Done
#TODO: потестировать все аргументы template_list Done
#TODO: добавить затраченное время в каждую проверку Done
#TODO: сдвинуть саждый оюъект влево Done
#TODO: пометить медленные методы как (slow) Done
#TODO: оптимизация Report List Done
#TODO: превратить функцию подсчета времени в декоратор Done
#TODO: реализовать проверку non-planar полигонов Done
#TODO: неравномерные ячейки сетки Done
#TODO: проверить что за подчеркнутые checkbox_list в этом файле Done
#TODO: проверить время выполнения пунктов группы Uvs Done
#TODO: UnfrozenTransforms переделать на конвертацию типа данных Done
#TODO: добавить диалог с требованием сохранить текущий файл Done
#TODO: поискать встроенный метод конвертации времени в привычный формат Done
#TODO: в финальном диалоговом окне неправильное время выполнения Done
#TODO: оптимизировать долгие проверки Done
#TODO: сбрасывать таймеры в начале сканирования Done
#TODO: стартовать progress bar перед первой задачей Done


import bpy
from bpy.app.handlers import persistent
from .__version__ import __version__
import time
from .mv_panels import *
from .checkers import *

#=======ATTRIBUTES==========
class CheckboxItem(bpy.types.PropertyGroup):
	'''Информация о каждой проверке'''
	def _collect_checkers(self, context):
		update_checkboxes_count()
	
	name : bpy.props.StringProperty(name="Name") # type: ignore
	group : bpy.props.StringProperty(name="Group") # type: ignore
	group_state : bpy.props.BoolProperty(default=False) # type: ignore
	state : bpy.props.BoolProperty(default=False, update=_collect_checkers, name="Select Check") # type: ignore
	color : bpy.props.StringProperty(default="GRAY", name="Red is Error and Yellow is Warning") # type: ignore
	warning_type : bpy.props.BoolProperty(default=False, name="Select Warning/Error") # type: ignore
	description : bpy.props.StringProperty(name="Description") # type: ignore
	time : bpy.props.StringProperty(name="Time", default="") # type: ignore


class CheckboxesCount(bpy.types.PropertyGroup):
	'''Количество включенных чекбоксов в каждой группе и в общей сумме'''
	group_name : bpy.props.StringProperty() # type: ignore
	active_count : bpy.props.IntProperty() # type: ignore
	group_length : bpy.props.IntProperty() # type: ignore
	all_active_count : bpy.props.IntProperty() # type: ignore


class IssuesCollection(bpy.types.PropertyGroup):
	'''Изначальное формирование отчета. Используется для формирования FormateReport и для бэкапа'''
	name : bpy.props.StringProperty() # type: ignore
	header : bpy.props.StringProperty() # type: ignore
	text : bpy.props.StringProperty() # type: ignore
	success : bpy.props.StringProperty(default="[SUCCESS]") # type: ignore
	hide_state : bpy.props.BoolProperty(default=True) # type: ignore


class FormateReport(bpy.types.PropertyGroup):
	'''Финально сформированный отчет. Нужен для возможности скрывать и отображать части отчета'''
	name : bpy.props.StringProperty() # type: ignore
	header : bpy.props.StringProperty() # type: ignore
	text : bpy.props.StringProperty() # type: ignore
	success : bpy.props.StringProperty(default="[SUCCESS]") # type: ignore
	hide_state : bpy.props.BoolProperty(default=True) # type: ignore


class AddonAttributes(bpy.types.PropertyGroup):
	'''Основные атрибуты аддона'''
	def _sort_by_color(self, context):
		main_sort_by_color(context)

	issue_index : bpy.props.IntProperty(default=2, name="Checked Issue") # type: ignore

	checkboxes : bpy.props.CollectionProperty(type=CheckboxItem) # type: ignore
	checkboxes_count : bpy.props.CollectionProperty(type=CheckboxesCount) # type: ignore

	hide_green : bpy.props.BoolProperty(default=True, update=_sort_by_color, description="Hide Sucessfil Checks") # type: ignore
	sort_by_color : bpy.props.BoolProperty(default=True, update=_sort_by_color, description="Sorting Checks by Color") # type: ignore

	spent_time : bpy.props.FloatProperty(default=0.0) # type: ignore
	progress_factor : bpy.props.FloatProperty(default=0.0) # type: ignore

	check_active : bpy.props.BoolProperty(name="Active Collection", default=True, description="Check all scene objects or Active Collection") # type: ignore


@persistent 
def pre_expand_checkboxes(scene):
	'''Первоначальная настройка аддона'''
	# ЧТОБЫ ОЧИСТИТЬ СПИСОК ЧЕКБОКСОВ НУЖНО РАСКОММЕНТИРОВАТЬ СТРОКИ НИЖЕ
	#getattr(bpy.context.scene.mv_attributes, "checkboxes").clear()

	# настройка аддона при первой инициализации
	initial_checkboxes = bpy.context.scene.mv_attributes.checkboxes

	# создание чекбоксов из словаря
	if len(initial_checkboxes) != len(checkbox_list):
		initial_checkboxes.clear()

		for item in checkbox_list:
			new_checkbox = initial_checkboxes.add()
			new_checkbox.name = item
			new_checkbox.group = checkbox_list[item]["group"]
			new_checkbox.group_state = False
			new_checkbox.state = False
			new_checkbox.color = 'GRAY'
			new_checkbox.description = checkbox_list[item]["info"]
			new_checkbox.time = ''
			if checkbox_list[item]["report"] == "warning":
				new_checkbox.warning_type = True
			else:
				new_checkbox.warning_type = False
	else: # проверка на соответсвие имени чекбокса словарю
		for ch_box, item in zip(initial_checkboxes, checkbox_list):
			if ch_box.name != item:
				ch_box.name = item
				ch_box.group = checkbox_list[item]["group"]
				ch_box.group_state = False
				ch_box.state = False
				ch_box.color = 'GRAY'
				ch_box.description = checkbox_list[item]["info"]
				ch_box.time = ''
				if checkbox_list[item]["report"] == "warning":
					ch_box.warning_type = True
				else:
					ch_box.warning_type = False
	
	update_checkboxes_count()


class SelectBad(bpy.types.Operator):
	'''Выбрать объект или элементы, которые не прошли проверку'''
	bl_idname = "object.select_bad"
	bl_label = "Select Bad"
	bl_description = "Select current Objects or Elements"

	elements : bpy.props.StringProperty() # type: ignore [object_name, "element_type", "elements_list"]

	def __select_collection(self, collection):
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		set_active_collection(bpy.context.view_layer.layer_collection, collection)
		#bpy.context.view_layer.active_layer_collection = layer_collection

	def __select_object(self, object):
		# выделяем и делаем активным объект сцены
		if bpy.context.mode != 'OBJECT':
			bpy.ops.object.mode_set(mode='OBJECT')

		bpy.ops.object.select_all(action='DESELECT')
		
		if object.name in bpy.context.view_layer.objects:
			bpy.context.view_layer.objects.active = object
			object.select_set(True)

			# фокусировка камеры вьбюпорта на активном объекте
			if bpy.context.area.type == 'VIEW_3D':
				bpy.ops.view3d.view_selected()
				#bpy.ops.view3d.view_pan(extend=True)

	def __select_elements(self, object, element_type, elements_set):
		if len(elements_set) == 0: return

		# переключаемся между объектами
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		if object.name in bpy.context.view_layer.objects:
			bpy.context.view_layer.objects.active = object
			object.select_set(True)
		
		# выделяем элементы
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_mode(type=element_type) # FACE, EDGE, VERT
		bpy.ops.mesh.select_all(action='DESELECT')
		bpy.ops.object.mode_set(mode='OBJECT')

		for element in elements_set:
			if element_type == "FACE":
				object.data.polygons[element].select = True
			elif element_type == "EDGE":
				object.data.edges[element].select = True
			elif element_type == "VERT":
				object.data.vertices[element].select = True
		
		bpy.ops.object.mode_set(mode='EDIT')

		# фокусировка камеры вьбюпорта на активном объекте
		if bpy.context.area.type == 'VIEW_3D':
			bpy.ops.view3d.view_selected()

	def execute(self, context):
		mesh_types = ["FACE", "EDGE", "VERT"]
		element_list = eval(self.elements)
		object_name = element_list[0]
		element_type = element_list[1]
		
		if element_type in mesh_types:
			elements_list = element_list[2]

			object = bpy.context.scene.objects[object_name]
			self.__select_elements(object, element_type, elements_list)
		else:
			if element_type == "COLL":
				self.__select_collection(bpy.data.collections[object_name])
			else:
				self.__select_object(bpy.context.scene.collection.all_objects[object_name])
		
		return {'FINISHED'}


class SelectCheckboxGroup(bpy.types.Operator):
	'''Выбор группы чекбоксов'''
	bl_idname = "object.select_checkboxes_button"
	bl_label = "Select Checkboxes"
	bl_description = "Select a group of checkboxes by button"
	bl_options = {'REGISTER', 'INTERNAL'}

	group_name: bpy.props.StringProperty() # type: ignore

	def execute(self, context):
		for item in context.scene.mv_attributes.checkboxes_count:
			if item.group_name == self.group_name:
				active_count = item.active_count
				group_length = item.group_length
				all_checkbox_count = item.all_active_count

		# выбираем чекбоксы по нажатии соответствующей кнопки
		for checkbox in context.scene.mv_attributes.checkboxes:
			if 0 < active_count < group_length:
				if checkbox.group == self.group_name:
					checkbox.state = True
			else:
				if checkbox.group == self.group_name:
					checkbox.state = not checkbox.state
		
		return {'FINISHED'}


class RunCheckboxGroup(bpy.types.Operator):
	'''Запуск проверки группы чекбоксов'''
	bl_idname = "object.run_checkboxes_button"
	bl_label = "Run complete Group of Checkboxes"
	bl_description = "Start checking all group items"
	bl_options = {'REGISTER', 'INTERNAL'}

	group_name: bpy.props.StringProperty() # type: ignore
	# def __init__(self):
	# 	bpy.types.Scene.group_name = self.group_name
	
	@if_scene_dirty
	def execute(self, context):
		group_name = self.group_name
		bpy.types.Scene.group_name = group_name

		start_time = time.time()
		# очищаем таймеры чекбоксов
		for item in bpy.context.scene.mv_attributes.checkboxes:
			item.time = ""
		
		context.scene.mv_attributes.spent_time = 0.0
		context.scene.issues.clear()
		context.scene.formate_report.clear()

		for i, item in enumerate(context.scene.mv_attributes.checkboxes):
			redraw_progress_bar(i)

			if item.group == bpy.types.Scene.group_name:
				reset_color_labels(context, item.name)
				start_single_check(context, item.name)

		context.scene.mv_attributes.progress_factor = 0.0

		# отображение диалогового окна
		if time.time() - start_time > 0.5: # отображать диалог через 0.5 попугаев
			bpy.ops.object.finish_dialog('INVOKE_DEFAULT')
		return {'FINISHED'}

class RunSingleCheck(bpy.types.Operator):
	'''Запуск единичной проверки'''
	bl_idname = "object.run_single_check"
	bl_label = "Run Single Check"
	bl_description = "Run single check"
	bl_options = {'REGISTER', 'INTERNAL'}

	
	check_type : bpy.props.StringProperty() # type: ignore
	# def __init__(self):
	# 	bpy.types.Scene.check_type = self.check_type

	@classmethod #@property
	def description(cls, context, properties):
		for item in checkbox_list:
			if item == properties.check_type:
				return checkbox_list[item]["info"]

	@if_scene_dirty
	def execute(self, context):
		#check_type = bpy.types.Scene.check_type
		try:
			check_type = self.check_type
			bpy.types.Scene.check_type = check_type
			context.scene.mv_attributes.spent_time = 0.0
			start_single_check(context, check_type)
		except:
			pass
		return {'FINISHED'}


class InvertCheckboxes(bpy.types.Operator):
	'''Инвертировать выбор чекбоксов'''
	bl_idname = "object.invert_checkboxes"
	bl_label = "Invert Checkboxes"
	bl_description = "Invert selected checks"
	bl_options = {'REGISTER', 'INTERNAL'}

	def execute(self, context):
		for item in context.scene.mv_attributes.checkboxes:
			item.state = not item.state
		return {'FINISHED'}


class CheckFailedOnly(bpy.types.Operator):
	'''Выбрать только failed проверки'''
	bl_idname = "object.check_failed_only"
	bl_label = "Check Failed Only"
	bl_description = "Select only failed checks"
	bl_options = {'REGISTER', 'INTERNAL'}

	def execute(self, context):
		# снимаем выбор со всех чекбоксов
		for item in context.scene.mv_attributes.checkboxes:
			item.state = False

		# выбираем только failed
		for item in context.scene.issues:
			if item.success == "[FAILED]":
				if item.name in context.scene.mv_attributes.checkboxes:
					context.scene.mv_attributes.checkboxes[item.name].state = True
		return {'FINISHED'}


class CheckAll(bpy.types.Operator):
	'''Выбрать все чекбоксы'''
	bl_idname = "object.check_all"
	bl_label = "Check All"
	bl_description = "Check all checks"
	bl_options = {'REGISTER', 'INTERNAL'}

	def execute(self, context):
		if context.scene.mv_attributes.checkboxes_count[0].all_active_count < len(checkbox_list):
			for item in context.scene.mv_attributes.checkboxes:
				item.state = True
		else:
			for item in context.scene.mv_attributes.checkboxes:
				item.state = False
		return {'FINISHED'}


class ClearAddon(bpy.types.Operator):
	'''Кнопка очистки всех данных аддона'''
	bl_idname = "object.clear_addon"
	bl_label = "Clear"
	bl_description = "Clear all addon's data"
	bl_options = {'REGISTER', 'INTERNAL'}

	def execute(self, context):
		# очищаем окно report
		context.scene.issues.clear()
		context.scene.formate_report.clear()

		# очищаем данные чекбоксов
		for item in context.scene.mv_attributes.checkboxes:
			#item.state = False
			item.color = "GRAY"
			item.time = ""

		return {'FINISHED'}


class RunChecksOnSelected(bpy.types.Operator):
	'''Запуск выбранных проверок'''
	bl_idname = "object.run_checks_on_selected"
	bl_label = "Run Checks On Selected"
	bl_description = "Check active collection"
	#bl_options = {'REGISTER', 'INTERNAL'}
	
	@if_scene_dirty
	def execute(self, context):
		# очищаем таймеры чекбоксов
		for item in bpy.context.scene.mv_attributes.checkboxes:
			item.time = ""
		
		bpy.context.scene.mv_attributes.spent_time = 0.0

		context.scene.issues.clear()
		context.scene.formate_report.clear()

		for i, item in enumerate(context.scene.mv_attributes.checkboxes):
			redraw_progress_bar(i)
			reset_color_labels(context, item.name)
			if item.state == True:
				start_single_check(context, item.name)

		context.scene.mv_attributes.progress_factor = 0.0

		# отображение диалогового окна
		bpy.ops.object.finish_dialog('INVOKE_DEFAULT')
		return {'FINISHED'}

@spent_timer
def start_single_check(context, check_type):
	for check_name, items in checkbox_list.items():
		if check_name == check_type:
			method_name = items["foo"]
			method = globals()[method_name]
			method(context, check_type)
	return check_type

	

classes = (
	CheckboxItem,
	CheckboxesCount,
	AddonAttributes,
	IssuesCollection,
	FormateReport,
	SaveDialog,
	FinishDialog,
	ISSUES_UL_ReportList,
	CheckListWindowPanel,
	ReportListPanel,
	SelectBad,
	SelectCheckboxGroup,
	RunCheckboxGroup,
	RunSingleCheck,
	InvertCheckboxes,
	CheckFailedOnly,
	CheckAll,
	ClearAddon,
	RunChecksOnSelected
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	
	bpy.app.handlers.load_post.append(pre_expand_checkboxes)
	bpy.types.Scene.mv_attributes = bpy.props.PointerProperty(type=AddonAttributes)
	bpy.types.Scene.issues = bpy.props.CollectionProperty(type=IssuesCollection)
	bpy.types.Scene.formate_report = bpy.props.CollectionProperty(type=FormateReport)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	
	del bpy.types.Scene.mv_attributes
	del bpy.types.Scene.issues
	del bpy.types.Scene.formate_report
	bpy.app.handlers.load_post.remove(pre_expand_checkboxes)

if __name__ == "__main__":
	register()