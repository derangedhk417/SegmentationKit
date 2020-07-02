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
from kivy.core.window      import Window

from kivy.utils import get_color_from_hex as hex_color

from Dataset           import Dataset
from CustomBoxLayout   import CustomBoxLayout
from CustomFloatLayout import CustomFloatLayout

import numpy as np

class ImageManager(ButtonBehavior, CustomFloatLayout):
	def __init__(self, *args, **kwargs):
		if 'padding' in kwargs:
			self.padding = kwargs['padding']
			del kwargs['padding']
		else:
			self.padding = [0, 0, 0, 0]

		super(ImageManager, self).__init__(*args, **kwargs)

		with self.canvas:
			Color(1, 1, 1, 1)
			self.image_rect = Rectangle(
				pos=self.pos, 
				size=self.size
			)

		self.is_loaded = False

		self.bind(size=self._update_dims, pos=self._update_dims)
		self.bind(on_press=self._click)
		Window.bind(mouse_pos=self._mouse_pos)


	def posInRect(self, pos, rpos, rsize):
		if pos[0] > rpos[0] and pos[0] < rpos[0] + rsize[0]:
			if pos[1] > rpos[1] and pos[1] < rpos[1] + rsize[1]:
				return True
		return False

	def _mouse_pos(self, inst, val):

		in_rect = self.posInRect(
			Window.mouse_pos,
			(self.display_x, self.display_y),
			(self.display_width, self.display_height)
		)

		if in_rect:
			if self.parent.is_zooming:
				Window.set_system_cursor('crosshair')
			elif self.parent.is_panning:
				Window.set_system_cursor('size_nwse')
		else:
			Window.set_system_cursor('arrow')


	def _click(self, inst):
		print(inst)
		print(self.last_touch)
		print("pos: %f, %f"%(self.last_touch.pos[0] - self.pos[0], self.last_touch.pos[1] - self.pos[1]))

	def _resize(self, size, pos):
		# We need to honor the desired padding for the image display, as 
		# well as the aspect ratio of the loaded image.

		# Take the larger dimension of the image and figure out what it 
		# needs to be to fit in the window.

		if self.is_loaded:
			largest   = max(self.img_size[0], self.img_size[1])
			w_largest = True if size[0] > size[1] else False

			if w_largest:
				display_height = size[1] - self.padding[1] - self.padding[3]
				display_width  = int(self.aspect * display_height)

				if display_width > size[0] - self.padding[0] - self.padding[2]:
					display_width  = size[0] - self.padding[0] - self.padding[2]
					display_height = int((1 / self.aspect) * display_width)
			else:
				display_width  = size[0] - self.padding[0] - self.padding[2]
				display_height = int((1 / self.aspect) * display_width)

				if display_height > size[1] - self.padding[1] - self.padding[3]:
					display_height = size[1] - self.padding[1] - self.padding[3]
					display_width  = int(self.aspect * display_height)
			
			# Calculate how to center the image.
			self.display_x = pos[0] + (size[0] // 2) - (display_width // 2)
			self.display_y = pos[1] + (size[1] // 2) - (display_height // 2)

			self.image_rect.size = (
				display_width, 
				display_height
			)

			self.image_rect.pos  = (
				self.display_x, 
				self.display_y
			)

			self.display_width  = display_width
			self.display_height = display_height

		else:
			self.image_rect.size = (
				size[0] - self.padding[0] - self.padding[2], 
				size[1] - self.padding[1] - self.padding[3]
			)

			self.display_width  = size[0] - self.padding[0] - self.padding[2]
			self.display_height = size[1] - self.padding[1] - self.padding[3]

			self.image_rect.pos  = (
				pos[0] + self.padding[0], 
				pos[1] + self.padding[1]
			)

			self.display_x = pos[0] + self.padding[0]
			self.display_y = pos[1] + self.padding[1]

	def _update_dims(self, inst, val):
		self._resize(inst.size, inst.pos)

	# Takes a numpy/cv2 image and displays it.
	def setImage(self, img):
		self.is_loaded  = True
		self.img_size   = (img.shape[1], img.shape[0])
		self.aspect     = img.shape[1] / img.shape[0]
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

		# Here we force a resize.
		self._resize(self.size, self.pos)


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
			border=(0, 0, 1, 0),
			padding=(3, 3, 4, 3)
		)

		self.add_widget(self.image_manager)

		self.zoom_button.bind(on_press=self._zoom_pressed)
		self.pan_button.bind(on_press=self._pan_pressed)

		self.is_zooming = False
		self.is_panning = False


	def _zoom_pressed(self, inst):
		if self.is_zooming:
			self.is_zooming = False
			self.zoom_button.background_color = self.saved_color
		else:
			self.saved_color = self.zoom_button.background_color
			self.zoom_button.background_color = hex_color('#616161')
			self.is_zooming = True
			self.is_panning = False
			self.pan_button.background_color = self.saved_color

		print("p: %s, z: %s"%(self.is_panning, self.is_zooming))

	def _pan_pressed(self, inst):
		if self.is_panning:
			self.is_panning = False
			self.pan_button.background_color = self.saved_color
		else:
			self.saved_color = self.pan_button.background_color
			self.pan_button.background_color = hex_color('#616161')
			self.is_panning = True
			self.is_zooming = False
			self.zoom_button.background_color = self.saved_color

		print("p: %s, z: %s"%(self.is_panning, self.is_zooming))

	def setImage(self, img):
		self.image_manager.setImage(img)
		

	