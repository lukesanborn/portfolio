import json
import math
from typing import List, Generator

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backend_bases import MouseEvent

from src.path import Path
from src.ui import Field


class Render:
    def __init__(self, paths: List[Path] = None, colors: List[str] = None):
        """
Render FRC game field to plot trajectory
        """
        self.paths = []
        self.lines = []
        self.field = Field(54, 27)
        self.fig, self.ax = self.field.create_field()
        if paths is not None or colors is not None:
            for path, color in zip(paths, colors):
                self.add_path(path, color)

        self._dragging_point = None
        self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)

        self.selected_path = None

        self.fig.canvas.mpl_connect('button_press_event', self._on_click)
        self.fig.canvas.mpl_connect('button_release_event', self._on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self._on_motion)

    def add_path(self, path, color):
        self.paths.append(path)
        # TODO plot points if not empty
        if path.data:
            x, y = zip(*path.data)
        else:
            x, y = [], []
        self.lines.append(self.ax.plot(x, y, color=color, marker="o")[0])

    def _current_path(self):
        return self.paths[self.selected_path]

    def get_selected_path(self):
        return self._current_path()

    def update_path(self, speed, decelerate, inplace):
        p = self._current_path()
        p.speed = speed
        p.decelerate = decelerate
        p.inplace = inplace

    def get_path(self):
        p = self._current_path()
        return p.speed, p.decelerate, p.inplace

    def _current_line(self):
        return self.lines[self.selected_path]

    def get_current_path_data(self):
        return vars(self._current_path())

    def _update_plot(self):
        if not self.lines:
            return None
        line = self._current_line()
        if not self._current_path().data:
            line.set_data([], [])
        else:
            x, y = zip(*self._current_path().data)
            # Add new plot
            # if not line:
            #     self.lines[self.selected_path], = self.ax.plot(x, y, color=self.color, marker="o")
            # Update current plot
            # else:
            line.set_data(x, y)
        self.fig.canvas.draw()

    def _add_point(self, x, y=None):
        if isinstance(x, MouseEvent):
            x, y = x.xdata, x.ydata
        self._current_path().add_point(x, y)
        return len(self._current_path().data) - 1

    def _find_neighbor_point(self, event):
        u""" Find point around mouse position
        :rtype: ((int, int)|None)
        :return: index of the point that is on the correct path
        """
        if self.selected_path is None:
            return None
        path = self._current_path()
        distance_threshold = 10.0
        nearest_point = None
        min_distance = math.sqrt(2 * (100 ** 2))
        for i, (x, y) in enumerate(path.data):
            distance = math.hypot(event.xdata - x, event.ydata - y)
            if distance < min_distance:
                min_distance = distance
                nearest_point = i
        if min_distance < distance_threshold:
            return nearest_point
        return None

    def _on_click(self, event):
        """ callback method for mouse click event
        :type event: MouseEvent
        """
        if event.inaxes not in [self.ax]:
            return None
        point = self._find_neighbor_point(event)

        # left click
        if event.button == 1:
            if point:
                self._dragging_point = point
            else:
                self._add_point(event)
            self._update_plot()
        # right click
        elif event.button == 3:
            if point:
                self._current_path().remove_point(point)
                self._update_plot()

    def _on_release(self, event):
        u""" callback method for mouse release event
        :type event: MouseEvent
        """
        if event.button == 1 and event.inaxes in [self.ax] and self._dragging_point:
            self._dragging_point = None
            self._update_plot()

    def _on_motion(self, event):
        u""" callback method for mouse motion event
        :type event: MouseEvent
        """
        if not self._dragging_point:
            return
        if event.xdata is None or event.ydata is None:
            return
        self._current_path().remove_point(self._dragging_point)
        self._dragging_point = self._add_point(event)
        self._update_plot()

    def _convert_points(self, path):
        """Get raw points and convert them to field units"""
        x, y = zip(*path.data)
        raw = np.column_stack([x, y])
        return self.field.scale_up(raw)

    def convert_points(self):
        for path in self.paths:
            path.data = self._convert_points(path).tolist()

    def reset_positions(self, color, speed: float, decelerate: bool, inplace: bool):
        """
Convert raw positions into feet and add path. Set color and speed for next path. Reset variables.
        """
        p = Path(speed=speed, decelerate=decelerate, inplace=inplace)
        if self.selected_path is not None:
            # prev = self.convert_points().tolist()
            p.add_point(*self._current_path().data[-1])
            # self._current_path().data = prev
        self.add_path(p, color)
        self.selected_path = len(self.paths) - 1

    def render(self):
        """
Render interactive plot
        """
        plt.show()


def paths_from_json(dir_name: str) -> Generator:
    with open(f"{dir_name}/paths.json", "r") as f:
        data = json.load(f)
    for path in data["paths"]:
        yield Path(data=path["data"], speed=path["_speed"], decelerate=path["decelerate"],
                   inplace=path["inplace"])


def paths_to_json(paths: List[Path], dir_name: str) -> None:
    output = [vars(p) for p in paths]
    with open(f"{dir_name}/paths.json", "w") as f:
        json.dump({"paths": output}, f, indent=4)
