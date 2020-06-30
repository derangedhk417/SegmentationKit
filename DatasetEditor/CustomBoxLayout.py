# Author:      Adam Robinson
# Description: This class extends the functionality of the BoxLayout class by
#              adding background color and a colored border as optional 
#              parameters.

from kivy.app             import App
from kivy.uix.boxlayout   import BoxLayout
from kivy.graphics        import Rectangle, Color, Line

from kivy.utils import get_color_from_hex as hex_color

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