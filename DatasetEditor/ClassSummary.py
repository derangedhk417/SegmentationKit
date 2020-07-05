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

		self.class0_button = Button(
			text='class 0', size_hint_y=None, height=30
		)
		self.class1_button = Button(
			text='class 1', size_hint_y=None, height=30
		)
		self.class2_button = Button(
			text='class 2', size_hint_y=None, height=30
		)
		self.class_select_dropdown.add_widget(self.class0_button)
		self.class_select_dropdown.add_widget(self.class1_button)
		self.class_select_dropdown.add_widget(self.class2_button)

		self.class0_button.bind(on_press=self._class_selected)
		self.class1_button.bind(on_press=self._class_selected)
		self.class2_button.bind(on_press=self._class_selected)

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

		self.editor_box.add_widget(self.class_select_button)
		self.editor_box.add_widget(self.name_input)
		self.editor_box.add_widget(self.comment_input)


		self.dropdown_activator = DropDownContourItem(
			class_color=hex_color('#000000'),
			index=-1,
			class_name='none'
		)

		self.l1 = DropDownContourItem(
			class_color=hex_color('#FF0000'),
			index=0,
			class_name='Test 1'
		)
		self.contour_select_dropdown.add_widget(self.l1)

		self.l2 = DropDownContourItem(
			class_color=hex_color('#00FF00'),
			index=1,
			class_name='Test 2'
		)
		self.contour_select_dropdown.add_widget(self.l2)

		self.l3 = DropDownContourItem(
			class_color=hex_color('#0000FF'),
			index=2,
			class_name='Test 3'
		)
		self.contour_select_dropdown.add_widget(self.l3)

		self.l1.bind(on_press=self._item_selected)
		self.l2.bind(on_press=self._item_selected)
		self.l3.bind(on_press=self._item_selected)

		self.dropdown_activator.bind(on_press=self._activator_pressed)

		self.add_widget(self.dropdown_activator)
		self.add_widget(self.editor_box)

		self.dropdown_open = False

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
		self.class_select_dropdown.dismiss()


	def _item_selected(self, inst):
		self.dropdown_activator.setProperties(
			inst.class_color, inst.index, inst.class_name
		)

		self.contour_select_dropdown.dismiss()
		self.dropdown_open = False

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


