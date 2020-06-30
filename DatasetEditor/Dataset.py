# Author:      Adam Robinson
# Description: This class handles all of the loading, saving and modification
#              of the dataset files and the dataset json file.

import os
import sys
import code
import cv2
import numpy
import json

class Dataset:
	def __init__(self, ext=None):
		if ext is None:
			self.valid_extensions = ['bmp', 'jpg', 'png', 'tiff']
		else:
			self.valid_extensions = ext

	def loadDirectory(self, path, update_callback):
		self.root_path = path

		# Load a list of files and filter out anything that isn't
		# an image.
		files = [f for f in os.listdir(path)]
		files = [f for f in files if os.path.isfile(os.path.join(path, f))]
		files = [f for f in files if f.split('.')[-1] in self.valid_extensions]

		n_files = len(files)
		print(n_files)
		f_idx   = 0

		# Figure out if there is a meta.json file in the diretory.
		self.meta_path = os.path.join(path, 'meta.json')

		if os.path.isfile(self.meta_path):
			self._loadMetaFile(self.meta_path)
		else:
			self.meta_structure = {'entries':{}, 'classes':{}}

		self.images = {}

		# Now we load everything that is in the meta structure.
		# Once that is done, we load any additional files.
		for k, v in self.meta_structure['entries'].items():
			img_path = os.path.join(self.root_path, k)

			if not os.path.isfile(img_path):
				raise Exception(
					"File \'%s\' is missing from the directory"%img_path
				)

			try:
				img = cv2.imread(img_path, cv2.IMREAD_COLOR)
			except Exception as ex:
				raise Exception(
					"Could not load file \'%s\'"%img_path
				) from ex

			self.images['k'] = img

			f_idx += 1
			update_callback(f_idx / n_files)

		# Now we load any files from the directory that aren't in the meta
		# file and add an entry for them.
		for file in files:
			if file not in self.images:
				img_path = os.path.join(self.root_path, file)
				try:
					img = cv2.imread(img_path, cv2.IMREAD_COLOR)
				except Exception as ex:
					raise Exception(
						"Could not load file \'%s\'"%img_path
					) from ex

				self.images[file] = img
				self.meta_structure[file] = {'class_idx': -1, 'comment': ''}

				f_idx += 1
				update_callback(f_idx / n_files)

		# By this point all of the image files should be in memory and
		# the meta structure should be setup.
		return self


	def _loadMetaFile(self, path):
		with open(path, 'r') as file:
			self.meta_structure = json.loads(file.read())