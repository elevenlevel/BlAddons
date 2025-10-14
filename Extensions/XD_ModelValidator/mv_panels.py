import bpy, json
from .mv_utilities import *

class ISSUES_UL_ReportList(bpy.types.UIList):
	'''Список пройденных проверок в панели Report'''
	'''
	@classmethod
	def item_height(self, context, item):
		print("item_height")
		# Calculate height based on the number of text lines in the item
		base_height = 30
		extra_lines = len(eval(item.text)) if item.text else 0
		return base_height + extra_lines * 20  # assuming 20 pixels per line
	'''
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
		el_type_dict = {"FACE": "faces", "EDGE": "edges", "VERT": "vertices"}
		color_icons_dict = {"[WARNING]" : "STRIP_COLOR_03", "[FAILED]" : "STRIP_COLOR_01", "[SUCCESS]" : "STRIP_COLOR_04"} # type: ignore
		icon_value = color_icons_dict[item.success]
		grid = layout.grid_flow(row_major=True, columns=1, align=True)

		header_row = grid.row(align=True)
		header_row.alignment = 'EXPAND'

		# заголовок с типом проверки
		# стрелка скрытия содержимого
		if item.success != "[SUCCESS]":
			header_row.prop(item, "hide_state", text="", icon="DISCLOSURE_TRI_RIGHT" if item.hide_state else "DISCLOSURE_TRI_DOWN", emboss=False)
		else:
			header_row.label(text="", icon="BLANK1")
		
		header_row.label(text=item.header, icon=icon_value)

		# отключаем скрытые элементы
		if item.hide_state: return
		
		text_json = json.loads(item.text)

		for line_item in text_json:
			object_name, element_type, type_icon = line_item["object"], line_item["mesh_type"], line_item["type_icon"]

			text_row = grid.row(align=True)
			text_row.alignment = 'LEFT'
			text_row.label(text=" └", icon="NONE")

			if element_type in el_type_dict:
				elements_list = line_item["element_list"]
				# преобразуем строку с номерами элементов в список чисел
				elements_list = list(map(int, elements_list[1:-1].split(", ")))
				
				name = "{}: {} {}".format(object_name, len(elements_list), el_type_dict[element_type])

				elements = str([object_name, element_type, elements_list])
				text_row.operator("object.select_bad", text=name, icon=type_icon, emboss=False).elements = elements
			else:
				elements = str([object_name, element_type])
				if "!!!" in object_name:
					#text_row.label(text=" " + line_item["issue_string"][2:], icon=type_icon)
					text_row.label(text=" " + line_item["issue_string"][2:], icon=type_icon)
				else:
					text_row.operator("object.select_bad", text=object_name, icon=type_icon, emboss=False).elements = elements


#===========================
def set_header_row(self, context, main_column, item):
	'''Заголовок блоков левой колонки'''
	group_name = item.group
	row_name = "RUN " + group_name.capitalize() # RUN GENERAL

	header_row = main_column.row(align=False)
	header_row.scale_y = 1.2

	# стрелка сворачивания блока
	column1 = header_row.column(align=True)
	column1.prop(item, "group_state", text="", icon='TRIA_RIGHT' if not getattr(item, "group_state") else 'TRIA_DOWN', emboss=False)

	# кнопка запуска проверки всего блока
	column2 = header_row.column(align=False)
	column2.operator("object.run_checkboxes_button", text=row_name, icon="NONE").group_name = group_name

	# чекбокс включения/выключения группы чекбоксов НЕ УДАЛЯТЬ! НУЖНО!
	group_check_icon = "RADIOBUT_ON" # значение по умолчанию

	for item in context.scene.mv_attributes.checkboxes_count:
		if item.group_name == group_name:
			active_count = item.active_count
			group_length = item.group_length
			all_checkbox_count = item.all_active_count
			
			if active_count == 0:
				group_check_icon = "RADIOBUT_OFF"
			elif active_count != 0 and active_count != group_length:
				group_check_icon = "HOLDOUT_OFF"
			else:
				group_check_icon = "RADIOBUT_ON"
			break
	
	column3 = header_row.column(align=True)
	column3.operator("object.select_checkboxes_button", text="", icon=group_check_icon, emboss=False).group_name = group_name
	column3.alignment = 'LEFT'

def set_check_row(self, context, main_column, item):
	'''Строка с чекбоксом левой колонки'''
	check_row = main_column.row(align=True)
	check_row.scale_y = 0.66

	# выбор типа проблемы
	warning_column = check_row.column(align=True)
	warning_column.alignment = 'LEFT'
	warning_column.prop(item, "warning_type", icon='EVENT_W' if item.warning_type else 'EVENT_E', expand=False, icon_only=True, emboss=False)

	# цветной лейбл
	icons = {"GRAY":"BLANK1", "GREEN":"STRIP_COLOR_04", "YELLOW":"STRIP_COLOR_03", "RED":"STRIP_COLOR_01"}
	label_column = check_row.column(align=True)
	label_column.alignment = 'LEFT'
	label_column.operator("object.run_single_check", text=item.name, icon=icons[item.color], emboss=False).check_type = item.name

	# пробел для отделения чекбокса от лейбла
	space_column = check_row.column(align=True)
	space_column.alignment = 'EXPAND'

	# время выполнения
	time_column = check_row.column(align=True)
	time_column.alignment = 'RIGHT'
	time_column.label(text=item.time + " ")
	
	# чекбокс
	check_column = check_row.column(align=True)
	check_column.alignment = 'RIGHT'
	#check_column.separator()
	check_column.prop(item, "state", text="")

class CheckListWindowPanel(bpy.types.Panel):
	'''Основное окно аддона'''
	bl_idname = "OBJECT_PT_check_list_window"
	bl_label = "Model Validator"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Model Validator"
	bl_description = "Part of the addon with basic controls"
	bl_options = {'DEFAULT_CLOSED'}

	def execute(self, context):
		return {'CANCELLED'}

	def draw(self, context):
		layout = self.layout
		# нижние кнопки левой колонки
		buttons_row = layout.row(align=True)
		buttons_row.alignment = 'CENTER'
		buttons_row.operator("object.invert_checkboxes", text="Invert", icon="NONE")
		buttons_row.operator("object.check_failed_only", text="Check Failed", icon="NONE")
		buttons_row.operator("object.check_all", text="(un)Check All", icon="NONE")

		groups = []
		for item in context.scene.mv_attributes.checkboxes:
			if item.group in groups:
				continue
			groups.append(item.group)

			set_header_row(self, context, layout, item)

			for checkbox in context.scene.mv_attributes.checkboxes:
				if item.group_state and checkbox.group == item.group:
					set_check_row(self, context, layout, checkbox)

class ReportListPanel(bpy.types.Panel):
	'''Окно с отчетом'''
	bl_idname = "OBJECT_PT_report_list"
	bl_label = "Report List"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Model Validator"
	bl_description = "Part of the addon with found problems"
	#bl_owner_id = "OBJECT_PT_check_list_window"
	#bl_options = {'DEFAULT_CLOSED', 'HIDE_HEADER', 'INSTANCED', 'HEADER_LAYOUT_EXPAND'}

	def draw_header(self, context):
		pass

	def draw(self, context):
		layout = self.layout

		# progress bar
		progress_row = layout.row(align=True)
		progress_row.alignment = 'EXPAND'
		progress_row.scale_y = 0.3
		if context.scene.mv_attributes.progress_factor != 0.0:
			progress_row.progress(text='', text_ctxt='', translate=True, factor=context.scene.mv_attributes.progress_factor, type='BAR')
		else:
			progress_row.label(text='')

		# кнопки Clear, Run и выбор что проверять
		buttons_row = layout.row(align=True)
		buttons_split_left = buttons_row.split(factor=1)
		buttons_split_center = buttons_row.split(factor=1)
		buttons_split_right = buttons_row.split(factor=1)

		buttons_split_left.operator("object.clear_addon", text="Clear")
		buttons_split_left.enabled = len(bpy.context.scene.issues) != 0
		buttons_split_left.scale_y = 1.2
		buttons_split_center.operator("object.run_checks_on_selected", text="Run", icon="NONE")
		buttons_split_center.enabled = False
		buttons_split_center.scale_y = buttons_split_left.scale_y

		buttons_split_right.prop(context.scene.mv_attributes, "check_active", text="Active", expand=True)
		buttons_split_right.scale_y = 1.2
		
		# активируем кнопку если хоть одна галочка включена
		if len(context.scene.mv_attributes.checkboxes_count) > 0:
			if context.scene.mv_attributes.checkboxes_count[0].all_active_count > 0:
				buttons_split_center.enabled = True
		
		# Список найденных проблем
		list_row = layout.row(align=True)

		list_row.template_list("ISSUES_UL_ReportList",
								list_id="sosiska",
								dataptr=bpy.context.scene, propname="formate_report",
								active_dataptr=context.scene.mv_attributes, active_propname="issue_index",
								type="DEFAULT",
								rows=10,
								maxrows=10,
								sort_reverse=False,
								sort_lock=True)
		
		checkbox_row = layout.row(align=True)

		checkbox_row.prop(context.scene.mv_attributes, "hide_green", text="Hide Green")
		checkbox_row.prop(context.scene.mv_attributes, "sort_by_color", text="Sort by Color")


class SaveDialog(bpy.types.Operator):
	'''Требование сохраниться если сцена не сохранена'''
	bl_idname = "object.save_dialog"
	bl_label = "Save"
	bl_description = "Save scene"
	bl_options = {'REGISTER', 'INTERNAL', 'BLOCKING'}

	def execute(self, context):
		save_scene()
		proceed_function = bpy.types.Scene.proceed_function
		proceed_function(self, context)
		bpy.types.Scene.proceed_function = None  # Очистить переменную после выполнения
		return {'FINISHED'}

	def invoke(self, context, event):
		#return self.invoke_confirm(context, event)
		return context.window_manager.invoke_confirm(self, event=event, icon="WARNING", confirm_text="Save", title="Scene is not saved!", message="Save scene?")

class FinishDialog(bpy.types.Operator):
	'''Финальный диалог с информацией о полном тайминге'''
	bl_idname = "object.finish_dialog"
	bl_label = "Done!"
	bl_description = "Finish dialog with spent time"
	bl_options = {'REGISTER', 'INTERNAL'}

	def execute(self, context):
		return {'FINISHED'}
	
	def invoke(self, context, event):
		checked_objects_count = len(select_check_entities("objects"))
		checked_collections_count = len(select_check_entities("collections"))

		float_time = context.scene.mv_attributes.spent_time
		good_time = convert_float_time(float_time)

		col_postfix = "collections" if checked_collections_count != 1 else "collection"
		obj_postfix = "objects" if checked_objects_count != 1 else "object"

		message = "Time spent: {}".format(good_time)
		message += "\n"
		message += "Checked: {} {}".format(checked_collections_count, col_postfix)
		message += "\n"
		message += "Checked: {} {}".format(checked_objects_count, obj_postfix)
		print('\a') # звук на финише
		return context.window_manager.invoke_confirm(self, event=event, title="Done!", message=message)