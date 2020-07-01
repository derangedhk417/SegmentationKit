# Author:      Adam Robinson
# Description: This file contains a class that displays an image while
#              handling resizing, events, zooming, panning and drawing
#              geometry on the image.

from kivy.uix.label        import Label
from kivy.uix.image        import Image
from kivy.uix.gridlayout   import GridLayout
from kivy.uix.behaviors    import ButtonBehavior
from kivy.core.image       import Image as CoreImage
from kivy.graphics.texture import Texture
from kivy.graphics         import Rectangle, Color, Line
from kivy.uix.scrollview   import ScrollView
from kivy.uix.button       import Button
from kivy.uix.floatlayout  import FloatLayout

from Dataset           import Dataset
from CustomBoxLayout   import CustomBoxLayout
from CustomFloatLayout import CustomFloatLayout

import numpy as np

class ImageManager(ButtonBehavior, CustomFloatLayout):
	def __init__(self, *args, **kwargs):
		super(ImageManager, self).__init__(*args, **kwargs)

		with self.canvas:
			Color(1, 1, 1, 1)
			self.image_rect = Rectangle(
				pos=self.pos, 
				size=self.size
			)

		self.bind(size=self._update_dims, pos=self._update_dims)

	def _update_dims(self, inst, val):
		self.image_rect.pos  = (inst.pos[0] + 10, inst.pos[1] + 10)
		self.image_rect.size = (inst.size[0] - 20, inst.size[1] - 20)

	# def _update_image_rect(self, instance, value):
	# 	self.image_rect.pos  = self.image.pos
	# 	self.image_rect.size = (self.image.size[0] - 1, self.image.size[1])

	# 	# if self.image_texture is not None:
	# 	# 	self.image_texture.size = (self.image.size[0] - 1, self.image.size[1])
	# 	print(self.image.size)
	# 	print(self.image.pos)

	# Takes a numpy/cv2 image and displays it.
	def setImage(self, img):
		self.img_size   = (img.shape[1], img.shape[0])
		self.img        = img
		self.img_buffer = np.fliplr(np.rot90(np.rot90(img)))
		self.img_buffer = memoryview(self.img_buffer.flatten())

		self.image_texture = Texture.create(size=self.img_size, colorfmt='bgr')
		self.image_texture.blit_buffer(
			self.img_buffer, 
			colorfmt='bgr', 
			bufferfmt='ubyte'
		)

		self.image_rect.texture = self.image_texture

class ImageDisplay(ButtonBehavior, CustomBoxLayout):
	def __init__(self, *args, **kwargs):
		super(ImageDisplay, self).__init__(*args, **kwargs)

		self.toolbar = CustomBoxLayout(
			orientation='horizontal',
			size_hint_y=None,
			height=50,
			padding=[5, 5, 5, 5],
			spacing=5,
			border=(0, 0, 1, 0)
		)

		self.zoom_button = Button(
			text='Zoom',
			size_hint_x=None,
			size_hint_y=1,
			width=70
		)

		self.pan_button = Button(
			text='Pan',
			size_hint_x=None,
			size_hint_y=1,
			width=70
		)

		self.toolbar.add_widget(self.pan_button)
		self.toolbar.add_widget(self.zoom_button)

		self.add_widget(self.toolbar)

		self.image_manager = ImageManager(
			border=(0, 0, 1, 0)
		)

		self.add_widget(self.image_manager)

	def setImage(self, img):
		self.image_manager.setImage(img)
		

	