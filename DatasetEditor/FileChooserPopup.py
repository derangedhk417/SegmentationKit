# Author:      Adam Robinson
# Description: This class acts as a folder chooser dialog that enforces the
#              requirement that the user choose a folder and not a file.


from kivy.uix.button      import Button
from kivy.uix.label       import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup       import Popup

from CustomBoxLayout import CustomBoxLayout

import os

class FileChooserPopup(Popup):
	def __init__(self, *args, **kwargs):
		self.main_layout    = CustomBoxLayout(
			orientation='vertical', padding=[3, 3, 3, 3]
		)
		self.chooser = FileChooserListView(
			path='~/', dirselect=True
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

		self.directory_chosen_callback = kwargs['callback']
		del kwargs['callback']

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
			self.directory_chosen_callback(self.chooser.selection[0])