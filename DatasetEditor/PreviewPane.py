# Author:      Adam Robinson
# Description: This file contains the preview pane that shows a list of
#              image thumbnails for the dataset. It also contains the
#              classes used to control the sub-elements inside the pane.

from kivy.uix.label        import Label
from kivy.uix.image        import Image
from kivy.uix.gridlayout   import GridLayout
from kivy.uix.behaviors    import ButtonBehavior
from kivy.core.image       import Image as CoreImage
from kivy.graphics.texture import Texture
from kivy.graphics         import Rectangle, Color, Line
from kivy.uix.scrollview   import ScrollView

from Dataset         import Dataset
from CustomBoxLayout import CustomBoxLayout
from ImageDisplay    import ImageDisplay

import numpy as np

# TODO: Figure out why this code is so ugly. There must be a better
#       way to achieve the desired effect.

# This is the list of images at the left of the screen that
# can be scrolled through to select an image to edit.
class PreviewPane(CustomBoxLayout):
	def __init__(self, *args, **kwargs):
		super(PreviewPane, self).__init__(*args, **kwargs)

		self.scroll_view  = ScrollView(
			size_hint=(1, None),
			do_scroll_y=True,
			do_scroll_x=False,
			size=self.size
		)
		self.layout = GridLayout(
			cols=1, 
			spacing=10, 
			size_hint_y=None,
			padding=[10, 10, 10, 10]
		)
		self.layout.bind(minimum_height=self.layout.setter('height'))

		self.scroll_view.add_widget(self.layout)
		self.add_widget(self.scroll_view)

		self.current_selected_obj = None

		self.bind(size=self._update_size)

	def _update_size(self, instance, value):
		self.scroll_view.height = self.height

	def getCorrectImageWidth(self):
		return self.size[0] - 22

	# This loads thumbnails from a dataset and displays them inside itself.
	def loadThumbnails(self, dataset):
		self.dataset = dataset
		for k, v in dataset.thumbnails.items():
			pt = PreviewThumbnail(
				dataset, k, self,
				orientation='vertical',
				color=(0.2, 0.2, 0.2, 1),
				border=(1, 1, 1, 1),
				border_color=(0.5, 0.5, 0.5, 1),
				size_hint_x=1,
				size_hint_y=None,
				height=dataset.thumbnail_size[1] + 20
			)
			self.layout.add_widget(pt)

	def setSelected(self, inst, key):
		if self.current_selected_obj is not None:
			self.current_selected_obj.changeBorderColor(None)
		self.current_selected_key = key
		self.current_selected_obj = inst
		inst.changeBorderColor((1, 0, 0, 1))

		self.parent.editor.display.image_display.setImage(
			self.dataset.images[key]
		)


class PreviewThumbnail(ButtonBehavior, CustomBoxLayout):
	def __init__(self, dataset, key, parent, *args, **kwargs):
		super(PreviewThumbnail, self).__init__(*args, **kwargs)

		self._parent_obj = parent
		self.key         = key

		self.label = Label(
			text=key, 
			size_hint_y=None, 
			height=20,
			size_hint_x=1
		)

		# For some reason the texture inside this inherits some of
		# its color from the background. We need to make it white for
		# the image to display correctly.
		self.image_holder = ImageHolder(
			dataset.thumbnails[key], 
			dataset.thumbnail_size,
			size_hint_y = None,
			size_hint_x = None,
			height      = dataset.thumbnail_size[1],
			width       = dataset.thumbnail_size[0],
			color       = (1, 1, 1, 1)
		)

		self.add_widget(self.label)
		self.add_widget(self.image_holder)

		self.bind(on_release=self._clicked)

	def _clicked(self, instance):
		self._parent_obj.setSelected(self, self.key)
		


class ImageHolder(CustomBoxLayout):
	def __init__(self, image_buffer, size, *args, **kwargs):
		super(ImageHolder, self).__init__(*args, **kwargs)

		self.image_size = size

		self.image_texture = Texture.create(size=size, colorfmt='bgr')
		self.image_texture.blit_buffer(
			image_buffer, 
			colorfmt='bgr', 
			bufferfmt='ubyte'
		)

		with self.canvas:
			self.image_rect = Rectangle(
				texture=self.image_texture, 
				pos=self.pos, 
				size=self.image_size
			)

		self.bind(
			size=self._update_rect, 
			pos=self._update_rect
		)

	def _update_rect(self, instance, value):
		self.image_rect.pos  = (instance.pos[0] + 1, instance.pos[1] + 1) 
		self.image_rect.size = instance.size





	
