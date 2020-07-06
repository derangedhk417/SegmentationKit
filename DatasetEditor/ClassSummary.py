# Author:      Adam Robinson
# Description: This file contains the part of the interface that has
#              a dropdown list of ccontours in the current image and allows the
#              user to edit properties of the currently selected contour.

from kivy.uix.label        import Label
from kivy.uix.image        import Image
from kivy.uix.gridlayout   import GridLayout
from kivy.uix.behaviors    import ButtonBehavior
from kivy.graphics.texture import Texture
from kivy.uix.button       import Button
from kivy.graphics         import Rectangle, Color, Line
from kivy.uix.scrollview   import ScrollView
from kivy.uix.dropdown     import DropDown
from kivy.uix.textinput    import TextInput

from kivy.utils import get_color_from_hex as hex_color

from Dataset         import Dataset
from CustomBoxLayout import CustomBoxLayout

import numpy as np


# This contains the interface components that allow the user to select
# the class of the current contour that they are editing. This also
# contains functionality for adding new classes.
class ClassSummary(CustomBoxLayout):
	def __init__(self, *args, **kwargs):
		super(ClassSummary, self).__init__(*args, **kwargs)

		# The first item in this panel should be a dropdown containing
		# all of the contours in the current image.
		self.contour_select_dropdown = DropDown()
		self.contour_select_dropdown.auto_dismiss = False

		self.editor_box = CustomBoxLayout(
			orientation='vertical',
			padding=[8, 8, 8, 8],
			spacing=5
		)

		self.class_select_dropdown = DropDown()
		self.class_select_dropdown.auto_dismiss = False

		self.class_select_button = Button(
			text='Select Class',
			size_hint_y=None,
			height=30
		)

		self.class_select_button.bind(on_press=self._class_select_pressed)

		self.name_input = TextInput(
			text='Item Name',
			multiline=False,
			size_hint_y=None,
			height=30
		)
		self.comment_input = TextInput(
			text='Comments',
			multiline=True,
			size_hint_y=None,
			height=120
		)

		self.name_input.bind(text=self._name_text_changed)
		self.comment_input.bind(text=self._comment_text_changed)

		self.editor_box.add_widget(self.class_select_button)
		self.editor_box.add_widget(self.name_input)
		self.editor_box.add_widget(self.comment_input)

		self.dropdown_activator = DropDownContourItem(
			class_color=hex_color('#000000'),
			index=-1,
			class_name='none'
		)

		self.dropdown_activator.bind(on_press=self._activator_pressed)

		self.add_widget(self.dropdown_activator)
		self.add_widget(self.editor_box)

		self.dropdown_open = False
		self.current_entry = None
		self.dataset       = None
		self.contours               = []
		self.contour_dropdown_items = []
		self.current_contour        = None
		self.class_names            = []
		self.class_buttons          = []

	def _name_text_changed(self, inst, val):
		self.current_contour['name'] = val

	def _comment_text_changed(self, inst, val):
		self.current_contour['comment'] = val

	def writeChangesToMemory(self):
		if self.current_entry is None:
			raise Exception("Nothing is currently being edited.")

		entry = self.dataset.meta_structure['entries'][self.current_key]
		for idx, contour in enumerate(self.contours):
			entry[idx]['class_idx'] = contour['class_idx']
			entry[idx]['name']      = contour['name']
			entry[idx]['comment']   = contour['comment']

	def clearCurrentEntry(self):
		if self.current_entry is not None:
			for item in self.contour_dropdown_items:
				self.contour_select_dropdown.remove_widget(item)

		self.contours               = []
		self.contour_dropdown_items = []

	def addContour(self, contour):
		item_class_idx   = contour['class_idx']
		item_class_color = self.dataset.meta_structure['classes'][item_class_idx]['color']
		item_class_name  = self.dataset.meta_structure['classes'][item_class_idx]['name']

		proper_name = item_class_name
		if contour['name'] != '':
			if not contour['name'].isspace():
				proper_name = self.current_contour['name']

		dropdown_item = DropDownContourItem(
			class_color=item_class_color,
			index=item_class_idx,
			class_name=proper_name
		)
		self.contour_select_dropdown.add_widget(dropdown_item)
		dropdown_item.bind(on_press=self._item_selected)

		self.contours.append(contour)
		self.contour_dropdown_items.append(dropdown_item)

	def setCurrentContour(self, contour):
		self.current_contour = contour
		item_class_idx   = contour['class_idx']
		item_class_color = self.dataset.meta_structure['classes'][item_class_idx]['color']
		item_class_name  = self.dataset.meta_structure['classes'][item_class_idx]['name']

		proper_name = item_class_name
		if self.current_contour['name'] != '':
			if not self.current_contour['name'].isspace():
				proper_name = self.current_contour['name']

		self.dropdown_activator.setProperties(
			item_class_color, item_class_idx, proper_name
		)

		self.name_input.text          = contour['name']
		self.comment_input.text       = contour['comment']
		self.class_select_button.text = item_class_name

		self.contour_select_dropdown.dismiss()
		self.dropdown_open = False

	def populateClassDropdown(self):
		for button in self.class_buttons:
			self.class_select_dropdown.remove_widget(button)

		self.class_names   = []
		self.class_buttons = []
		for _class in self.dataset.meta_structure['classes']:
			self.class_names.append(_class['name'])
			button = Button(
				text=_class['name'], size_hint_y=None, height=30
			)
			self.class_buttons.append(button)
			self.class_select_dropdown.add_widget(button)
			button.bind(on_press=self._class_selected)

	def setCurrentEntry(self, key, dataset):
		if self.current_entry is not None:
			self.clearCurrentEntry()


		self.dataset       = dataset
		self.current_entry = self.dataset.meta_structure['entries'][key]
		self.current_key   = key

		self.populateClassDropdown()

		# Add each of these to the internal structure, and therefore the
		# image display.
		for contour in self.current_entry:
			self.addContour(contour)

		if len(self.current_entry) > 0:
			self.setCurrentContour(self.current_entry[0])

	def _activator_pressed(self, inst):
		if not self.dropdown_open:
			self.contour_select_dropdown.open(inst)
			self.dropdown_open = True
		else:
			self.dropdown_open = False
			self.contour_select_dropdown.dismiss()

	def _class_select_pressed(self, inst):
		self.class_select_dropdown.open(inst)

	def _class_selected(self, inst):
		self.class_select_button.text = inst.text
		self.current_contour['class_idx'] = self.class_names.index(inst.text)
		self.class_select_dropdown.dismiss()

		# We need to change the item in the dropdown list of contours to match.
		class_idx   = self.class_names.index(inst.text)
		contour_idx = self.contours.index(self.current_contour)
		item_class_color = self.dataset.meta_structure['classes'][class_idx]['color']
		item_class_name  = self.dataset.meta_structure['classes'][class_idx]['name']

		proper_name = item_class_name
		if self.current_contour['name'] != '':
			if not self.current_contour['name'].isspace():
				proper_name = self.current_contour['name']

		self.contour_dropdown_items[contour_idx].setProperties(
			item_class_color, self.class_names.index(inst.text), proper_name
		)

		self.dropdown_activator.setProperties(
			item_class_color, self.class_names.index(inst.text), proper_name
		)

		self.parent.display.image_display.setContourColor(contour_idx, item_class_color)

	def _item_selected(self, inst):
		idx = self.contour_dropdown_items.index(inst)
		contour = self.contours[idx]

		self.setCurrentContour(contour)

		

# This is a custom listbox item that displays the necessary information
# about a contour in the list box.
class DropDownContourItem(ButtonBehavior, CustomBoxLayout):
	def __init__(self, *args, **kwargs):
		self.class_color = kwargs['class_color']
		self.index       = kwargs['index']
		self.class_name  = kwargs['class_name']

		del kwargs['class_color']
		del kwargs['index']
		del kwargs['class_name']


		kwargs['orientation'] = 'horizontal'
		kwargs['size_hint_y'] = None
		kwargs['color']       = hex_color('#222222')
		kwargs['height']      = 36
		kwargs['border']      = (1, 1, 1, 1)
		kwargs['padding']     = (1, 1, 1, 1)

		super(DropDownContourItem, self).__init__(*args, **kwargs)

		# We want to display the color of this item in a box on the
		# left of the button. After this, we want the index of the item
		# and then the class of the item.

		self.color_box = CustomBoxLayout(
			height=34,
			size_hint_y=None,
			width=47,
			size_hint_x=None,
			border=(8, 8, 9, 8),
			color=self.class_color
		)

		self.index_box = CustomBoxLayout(
			height=34,
			size_hint_y=None,
			width=47,
			color=hex_color('#222222'),
			size_hint_x=None,
			border=(0, 0, 1, 0)
		)

		self.index_label = Label(text=str(self.index))
		self.index_box.add_widget(self.index_label)

		self.class_label_box = CustomBoxLayout(
			height=34,
			color=hex_color('#222222'),
			size_hint_y=None
		)

		self.class_label = Label(text=self.class_name)
		self.class_label_box.add_widget(self.class_label)

		self.add_widget(self.color_box)
		self.add_widget(self.index_box)
		self.add_widget(self.class_label_box)

	def setProperties(self, color, index, name):
		self.color_box.updateColor(color)
		self.index_label.text = str(index)
		self.class_label.text = name


