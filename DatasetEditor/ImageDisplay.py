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
from kivy.graphics         import Rectangle, Color, Line, InstructionGroup
from kivy.uix.scrollview   import ScrollView
from kivy.uix.button       import Button
from kivy.uix.floatlayout  import FloatLayout
from kivy.core.window      import Window

from kivy.utils import get_color_from_hex as hex_color

from Dataset           import Dataset
from CustomBoxLayout   import CustomBoxLayout
from CustomFloatLayout import CustomFloatLayout

import numpy as np
import code

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
		self.bind(
			on_touch_down=self._down,
			on_touch_up=self._up,
			on_touch_move=self._move
		)
		Window.bind(mouse_pos=self._mouse_pos)

		self.click_down            = False
		self.drag_start            = (0, 0)
		self.drag_w                = 0
		self.drag_h                = 0
		self.current_zoom_rect_obj = None

		self.current_zoom_subarray = None
		self.last_zoom_coordinates = None


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
		else:
			Window.set_system_cursor('arrow')


	def _down(self, inst, val):
		view_x = val.pos[0] - self.display_x
		view_y = val.pos[1] - self.display_y

		in_rect = self.posInRect(
			Window.mouse_pos,
			(self.display_x, self.display_y),
			(self.display_width, self.display_height)
		)

		if in_rect and self.is_loaded:
			self.click_down = True
			self.drag_start = Window.mouse_pos

	def _up(self, inst, val):
		self.click_down = False

		if self.current_zoom_rect_obj is not None:
			self.canvas.remove(self.current_zoom_rect_obj)

		in_rect = self.posInRect(
			Window.mouse_pos,
			(self.display_x, self.display_y),
			(self.display_width, self.display_height)
		)

		if in_rect and self.parent.is_zooming:
			# See if they selected a reasonably large area.
			if np.abs(self.drag_w * self.drag_h) > 16:
				# The selected at least a 4x4 region, consider this a zoom in.
				# Calculate the coordinates in the image, of the zoom.
				zoom_x0 = self.drag_start[0] - self.display_x
				zoom_y0 = self.drag_start[1] - self.display_y

				zoom_x1 = val.pos[0] - self.display_x
				zoom_y1 = val.pos[1] - self.display_y

				# If the user dragged backwards on any axis, the 
				# coordinates may need to be exhanged.
				if zoom_x0 > zoom_x1:
					t = zoom_x1
					zoom_x1 = zoom_x0
					zoom_x0 = t

				if zoom_y0 > zoom_y1:
					t = zoom_y1
					zoom_y1 = zoom_y0
					zoom_y0 = t

				self.zoomTo(zoom_x0, zoom_x1, zoom_y0, zoom_y1)
				self.drag_start            = (0, 0)
				self.drag_w                = 0
				self.drag_h                = 0

	def _move(self, inst, val):
		if self.click_down:
			if self.parent.is_zooming:
				pos    = Window.mouse_pos
				self.drag_w = pos[0] - self.drag_start[0]
				self.drag_h = pos[1] - self.drag_start[1] 

				if self.current_zoom_rect_obj is not None:
					self.canvas.remove(self.current_zoom_rect_obj)

				self.current_zoom_rect_obj = InstructionGroup()
				self.current_zoom_rect_obj.add(Color(0, 0, 0, 1))
				self.current_zoom_rect_obj.add(Line(
					rectangle=(
						self.drag_start[0],  
						self.drag_start[1], 
						self.drag_w, 
						self.drag_h
					),
					dash_length=5,
					dash_offset=5,
					width=1
				))
				self.canvas.add(self.current_zoom_rect_obj)

		view_x = val.pos[0] - self.display_x
		view_y = val.pos[1] - self.display_y
		
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

	def zoomTo(self, x0, x1, y0, y1):
		# First, select the part of the image data that corresponds to the zoom
		# rectangle.
		if self.current_zoom_subarray is not None:
			to_zoom = self.current_zoom_subarray
		else:
			to_zoom = self.img

		# Convert screen coordinates to array indices
		x0_idx = int((x0 / self.display_width) * to_zoom.shape[1])
		x1_idx = int((x1 / self.display_width) * to_zoom.shape[1])
		y0_idx = int((y0 / self.display_height) * to_zoom.shape[0])
		y1_idx = int((y1 / self.display_height) * to_zoom.shape[0])

		# Account for the different coordinate system.
		y0_idx = to_zoom.shape[0] - y0_idx
		y1_idx = to_zoom.shape[0] - y1_idx

		self.current_zoom_subarray = to_zoom[
			y1_idx:y0_idx + 1,
			x0_idx:x1_idx + 1,
			:
		]

		self.last_zoom_coordinates = [
			x0_idx, x1_idx, y0_idx, y1_idx
		]

		self.img_size = (
			self.current_zoom_subarray.shape[1],
			self.current_zoom_subarray.shape[0]
		)
		self.aspect     = self.current_zoom_subarray.shape[1]
		self.aspect    /= self.current_zoom_subarray.shape[0]
		self.img_buffer = np.fliplr(np.rot90(np.rot90(self.current_zoom_subarray)))
		self.img_buffer = memoryview(self.img_buffer.flatten())

		#code.interact(local=locals())

		self.image_texture = Texture.create(
			size=self.img_size, 
			colorfmt='bgr'
		)
		self.image_texture.blit_buffer(
			self.img_buffer, 
			colorfmt='bgr', 
			bufferfmt='ubyte'
		)

		self.image_rect.texture = self.image_texture

		# Here we force a resize.
		self._resize(self.size, self.pos)

	def reset(self):
		if self.is_loaded:
			self.current_zoom_subarray = None
			self.setImage(self.img)


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


		self.reset_button = Button(
			text='Reset',
			size_hint_x=None,
			size_hint_y=1,
			width=70
		)

		self.toolbar.add_widget(self.zoom_button)
		self.toolbar.add_widget(self.reset_button)

		self.add_widget(self.toolbar)

		self.image_manager = ImageManager(
			border=(0, 0, 1, 0),
			padding=(3, 3, 4, 3)
		)

		self.add_widget(self.image_manager)

		self.zoom_button.bind(on_press=self._zoom_pressed)
		self.reset_button.bind(on_press=self._reset_pressed)

		self.is_zooming = False

	def _reset_pressed(self, inst):
		self.image_manager.reset()

	def _zoom_pressed(self, inst):
		if self.is_zooming:
			self.is_zooming = False
			self.zoom_button.background_color = self.saved_color
		else:
			self.saved_color = self.zoom_button.background_color
			self.zoom_button.background_color = hex_color('#616161')
			self.is_zooming = True

	

	def setImage(self, img):
		self.image_manager.setImage(img)
		

	