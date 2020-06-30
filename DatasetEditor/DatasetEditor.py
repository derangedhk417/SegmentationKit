# Author:      Adam Robinson
# Description: This file contains the core program logic and some of the 
#              interface components. More complicated interface components
#              are contained in other files.

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
from kivy.uix.progressbar import ProgressBar
from kivy.config          import Config
from kivy.clock           import Clock
from kivy.utils           import get_color_from_hex as hex_color

import code
import os
import threading

from CustomBoxLayout  import CustomBoxLayout
from FileChooserPopup import FileChooserPopup
from Dataset          import Dataset

# ---------------------------------------------------------
# Simple Interface Components
# ---------------------------------------------------------

# This is the menu at the top of the screen with the "Load"
# and "Save" buttons.
class TopMenu(CustomBoxLayout):
	def __init__(self, *args, **kwargs):
		self._parent_obj = kwargs['parent']
		del kwargs['parent']

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

		self.load_progress    = ProgressBar(max=100)
		self.current_progress = 0

		# TODO: Encapsulate this kind of functionality in a reusable class.
		def load_files(path):
			print("Loading: %s"%path)
			self.load_progress.opacity = 1

			def _inner_load(path):
				def progress_callback(n):
					self.current_progress = int(n * 100)
				dataset = Dataset().loadDirectory(path, progress_callback)
				self._parent_obj.dataset = dataset
				
			t = threading.Thread(target=_inner_load, args=(path,))
			t.start()

			def _check_process(b):
				self.load_progress.value = self.current_progress
				if not t.is_alive():
					Clock.unschedule(_check_process)
					self.load_progress.opacity = 0

			Clock.schedule_interval(_check_process, .1)

			

		self.load_popup = FileChooserPopup(
			title='Load File', callback=load_files
		)

		self.add_widget(self.open_button)
		self.add_widget(self.save_button)
		self.add_widget(self.load_progress)
		self.load_progress.opacity = 0

		self.open_button.bind(on_press=self._open_pressed)

		

	def _open_pressed(self, instance):
		self.load_popup.open()

# This is the list of images at the left of the screen that
# can be scrolled through to select an image to edit.
class PreviewPane(CustomBoxLayout):
	def __init__(self, *args, **kwargs):
		super(PreviewPane, self).__init__(*args, **kwargs)

		self.label = Label(text='Preview Pane')
		self.add_widget(self.label)

# This is the interface item that displays the image that is
# being edited, as well as some of the editing controls.
class Display(CustomBoxLayout):
	def __init__(self, *args, **kwargs):
		super(Display, self).__init__(*args, **kwargs)

		self.label = Label(text='display')
		self.add_widget(self.label)

# This contains the interface components that allow the user to select
# the class of the current contour that they are editing. This also
# contains functionality for adding new classes.
class ClassSummary(CustomBoxLayout):
	def __init__(self, *args, **kwargs):
		super(ClassSummary, self).__init__(*args, **kwargs)

		self.label = Label(text='class summary')
		self.add_widget(self.label)

# This is the parent component for the images display and the class
# summary.
class Editor(CustomBoxLayout):
	def __init__(self, *args, **kwargs):
		super(Editor, self).__init__(*args, **kwargs)

		self.splitter = Splitter(
			sizable_from = 'right',
			strip_size   = '7pt',
			min_size     = 100,
			max_size     = 10000
		)
		self.display       = Display()
		self.class_summary = ClassSummary()
		self.splitter.add_widget(self.display)
		self.add_widget(self.splitter)
		self.add_widget(self.class_summary)	

# Parent component for the preview pane and the editor.
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

# ---------------------------------------------------------
# Root Component
# ---------------------------------------------------------

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
			border=(0, 0, 0, 1),
			parent=self
		)
		self.interface = Interface(
			orientation='horizontal'
		)

		self.root.add_widget(self.top_menu)
		self.root.add_widget(self.interface)

		return self.root


if __name__ == '__main__':
	# This disables multitouch emulation.
	Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
	DatasetEditor().run()