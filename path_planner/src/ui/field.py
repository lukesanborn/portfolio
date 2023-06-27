import ctypes

import numpy as np
from matplotlib import pyplot as plt
from typing import Tuple, Any

ctypes.windll.shcore.SetProcessDpiAwareness(True)


class Field:
    def __init__(self, length: float = 54, width: float = 27, img_path: str = "images/cropped_field.jpg"):
        """
Create the 2022 FRC Field
        :param length: length of field in feet
        :param width: length of field of inches
        :param img_path: path of field image
        """
        self.length = length
        self.width = width
        self.img_path = img_path
        self.scale = 1

    def add_image(self, ax):
        """
Add image to plot and set scale factors
        :param ax: axis
        """
        img = plt.imread(self.img_path)
        ax.imshow(img)
        _, xmax, ymin, _ = plt.axis()
        self.scale = self.length / xmax

    def create_field(self) -> Tuple[Any, Any]:
        """
Create the matplotlib FRC Field and set scale factor
        :return: subplot with image
        """
        fig, ax = plt.subplots(sharex=True)
        self.add_image(ax)
        return fig, ax

    def scale_up(self, xy: np.array) -> np.array:
        """
Scale up field units to feet
        :param xy: (x,y) in field units (px)
        :return: feet
        """
        return xy * self.scale

    def scale_down(self, xy: np.array) -> np.array:
        """
Scale down feet to field units
        :param xy: (x,y) in feet
        :return: field units (px)
        """
        return xy / self.scale
