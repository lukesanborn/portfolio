import itertools
from typing import Optional, List

import numpy as np


class Path:
    id_iter = itertools.count()

    def __init__(self, data: Optional[list] = None, speed: float = -7.0, decelerate: bool = True,
                 inplace: bool = False):
        self.id = next(Path.id_iter)
        self.speed = speed
        self.inplace = inplace
        self.decelerate = decelerate
        if data is None:
            data = []
        self.data = data

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        if value < -12 or value > 12:
            raise ValueError("Speed out of range")
        self._speed = value

    def add_points(self, points: List[list]):
        self.data += points

    def add_point(self, x: float, y: float):
        self.data.append([x, y])

    def remove_point(self, i: int):
        self.data.pop(i)

    def to_numpy(self):
        return np.array(self.data)

    def __repr__(self):
        return f"Path {self.id}"
