from kivy.app             import App
from kivy.uix.boxlayout   import BoxLayout
from kivy.uix.slider      import Slider
from kivy.uix.widget      import Widget
from kivy.graphics        import Rectangle, Color, Line
from kivy.uix.button      import Button
from kivy.uix.splitter    import Splitter
from kivy.uix.label       import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup       import Popup
from kivy.config          import Config

from kivy.utils import get_color_from_hex as hex_color

# This disables multitouch emulation.
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

import code
import os

class CustomBoxLayout(BoxLayout):
	def __init__(self, *args, **kwargs):
		if 'color' in kwargs:
			self.background_color = kwargs['color']
			del kwargs['color']
		else:
			self.background_color = hex_color("#333333")

		if 'border_color' in kwargs:
			self.border_color = kwargs['border_color']
			del kwargs['border_color']
		else:
			self.border_color = hex_color("#595959")

		# left, top, right, bottom
		if 'border' in kwargs:
			self.border = kwargs['border']
			if not isinstance(self.border, tuple):
				self.border = tuple([self.border]*4)
			del kwargs['border']
		else:
			self.border = (0, 0, 0, 0)

		super(CustomBoxLayout, self).__init__(*args, **kwargs)

		with self.canvas.before:
			Color(*self.border_color)
			self.border_rect = Rectangle(size=self.size, pos=self.pos)

			Color(*self.background_color)
			p, s = self._get_background_rect(self.pos, self.size)

			self.rect = Rectangle(pos=p, size=s)

		self.bind(
			size=self._update_rect, 
			pos=self._update_rect
		)

	def _update_rect(self, instance, value):
		self.border_rect.pos  = instance.pos
		self.border_rect.size = instance.size

		p, s = self._get_background_rect(instance.pos, instance.size)
		self.rect.pos  = p
		self.rect.size = s

	def _get_background_rect(self, pos, size):
		left, top, right, bottom = self.border

		bg_pos  = [pos[0],   pos[1]]
		bg_size = [size[0], size[1]]

		bg_pos[0]  += left
		bg_size[0] -= left
		bg_pos[1]  += bottom
		bg_size[1] -= bottom

		bg_size[0] -= right
		bg_size[1] -= top


		return bg_pos, bg_size

class TopMenu(CustomBoxLayout):
	def __init__(self, *args, **kwargs):
		super(TopMenu, self).__init__(*args, **kwargs)

		self.open_button = Button(
			text='Load', 
			width=70,
			size_hint_x=None
		)
		self.save_button = Button(
			text='Save', 
			width=70,
			size_hint_x=None
		)

		self.load_popup = FileChooserPopup(
			title='Load File'
		)

		self.add_widget(self.open_button)
		self.add_widget(self.save_button)

		self.open_button.bind(on_press=self._open_pressed)

	def _open_pressed(self, instance):
		self.load_popup.open()

class PreviewPane(CustomBoxLayout):
	def __init__(self, *args, **kwargs):
		super(PreviewPane, self).__init__(*args, **kwargs)

		self.label = Label(text='Preview Pane')
		self.add_widget(self.label)

class Display(CustomBoxLayout):
	def __init__(self, *args, **kwargs):
		super(Display, self).__init__(*args, **kwargs)

		self.label = Label(text='display')
		self.add_widget(self.label)

class ClassSummary(CustomBoxLayout):
	def __init__(self, *args, **kwargs):
		super(ClassSummary, self).__init__(*args, **kwargs)

		self.label = Label(text='class summary')
		self.add_widget(self.label)

class Editor(CustomBoxLayout):
	def __init__(self, *args, **kwargs):
		super(Editor, self).__init__(*args, **kwargs)

		self.splitter = Splitter(
			sizable_from = 'right',
			strip_size   = '10pt',
			min_size     = 10,
			max_size     = 10000
		)
		self.display       = Display()
		self.class_summary = ClassSummary()
		self.splitter.add_widget(self.display)
		self.add_widget(self.splitter)
		self.add_widget(self.class_summary)	

class Interface(CustomBoxLayout):
	def __init__(self, *args, **kwargs):
		super(Interface, self).__init__(*args, **kwargs)

		self.preview_pane = PreviewPane(
			orientation='vertical', 
			size_hint_x=1,
			border=(0, 0, 1, 0)
		)
		self.editor = Editor(
			size_hint_x=4
		)
		self.add_widget(self.preview_pane)
		self.add_widget(self.editor)

class FileChooserPopup(Popup):
	def __init__(self, *args, **kwargs):
		self.main_layout    = CustomBoxLayout(
			orientation='vertical', padding=[3, 3, 3, 3]
		)
		self.chooser = FileChooserListView(
			path='~/', show_hidden=True, dirselect=True
		)
		self.bottom_buttons = CustomBoxLayout(
			orientation='horizontal',
			size_hint_y=None,
			height=40,
			padding=[2, 0, 2, 0]
		)

		self.load_button   = Button(text='Load')
		self.cancel_button = Button(text='Cancel')
		self.bottom_buttons.add_widget(self.cancel_button)
		self.bottom_buttons.add_widget(self.load_button)

		self.main_layout.add_widget(self.chooser)
		self.main_layout.add_widget(self.bottom_buttons)

		self.cancel_button.bind(on_press=self._cancel_pressed)
		self.load_button.bind(on_press=self._load_pressed)

		kwargs['content'] = self.main_layout

		super(FileChooserPopup, self).__init__(*args, **kwargs)

		# Create a popup for notifying the user that they need to select
		# a directory (not a file).
		self.notify_layout = CustomBoxLayout(orientation='vertical')
		self.close_button  = Button(text="Ok", size_hint_y=1)
		self.label         = Label(
			text='Please Choose a Directory (Not a file)', 
			size_hint_y=5, font_size=20
		)
		self.notify_layout.add_widget(self.label)
		self.notify_layout.add_widget(self.close_button)
		self.close_button.bind(on_press=self._close_notify_pressed)

		self.notify_popup = Popup(
			title='Invalid Choice', 
			content=self.notify_layout,
			size_hint=(None, None),
			size=(400, 200)
		)

	def _cancel_pressed(self, instance):
		self.dismiss()

	def _close_notify_pressed(self, instance):
		self.notify_popup.dismiss()

	def _load_pressed(self, instance):
		# self.chooser.path is the path to the directory that they selected.
		print(self.chooser.path)
		print(self.chooser.selection)
		if not os.path.isdir(self.chooser.selection[0]):
			self.notify_popup.open()
		else:
			self.dismiss()

class DatasetEditor(App):
	def __init__(self, *args, **kwargs):
		super(DatasetEditor, self).__init__(*args, **kwargs)

	def build(self):
		self.root      = BoxLayout(orientation='vertical')
		self.top_menu  = TopMenu(
			orientation='horizontal', 
			height=40, 
			size_hint_y=None,
			padding=[5, 5, 5, 5],
			border=(0, 0, 0, 1)
		)
		self.interface = Interface(
			orientation='horizontal'
		)

		self.root.add_widget(self.top_menu)
		self.root.add_widget(self.interface)

		return self.root


if __name__ == '__main__':
	DatasetEditor().run()