import math
from typing import Optional

from matplotlib import pyplot as plt
import scipy.interpolate
import scipy
import numpy as np
from scipy.interpolate import interp1d

from src.ui import Field
from src.utils import calculate_distance, calculate_heading, calculate_heading_rate, calculate_angle, wrap_angle
from src.utils import feet_inch
from src.utils import next_path
from src.utils import delta_distance


class Trajectory:

    def __init__(self, positions: np.array, path_name: str, loop_time: float = 0.02, speed: float = 5.0,
                 decelerate_constant: float = 1, points: int = 500):
        """
        Calculate the trajectory from a list of positions

        :param decelerate_constant: distance in feet from edge of path to begin decelerating
        :param positions: list of points (x,y)
        :param loop_time: time in seconds of each loop count
        :param speed: feet per second command
        :param points: points in first interpolation
        """
        self.path_name = path_name
        self.decelerate_constant = decelerate_constant
        self.positions = positions
        if speed < 0:
            self.negative_speed = True
            self.speed = abs(speed)
        else:
            self.negative_speed = False
        self.speed = abs(speed)
        self.loop_time = loop_time
        self.points = points

    def _interpolate(self, x: np.array, y: np.array, kind: str = "cubic") -> np.array:
        """
        Interpolates selected points on curve
        :param kind: type of interpolation
        :return: 2d array of points y, x
        """
        path_t = np.linspace(0, 1, x.size)
        r = np.vstack((x.reshape((1, x.size)), y.reshape((1, y.size))))
        spline = scipy.interpolate.interp1d(path_t, r, kind=kind)
        t = np.linspace(np.min(path_t), np.max(path_t), self.points)
        r = spline(t)
        return r.T

    def _pchip_interpolator(self, x: np.array, y: np.array) -> np.array:
        """
PCHIP 1-D monotonic cubic interpolation.
        :return: np.array of interpolated points y
        """
        path_t = np.linspace(0, 1, x.size)
        r = np.vstack((x.reshape((1, x.size)), y.reshape((1, y.size))))
        spline = scipy.interpolate.PchipInterpolator(path_t, r, axis=1)
        t = np.linspace(np.min(path_t), np.max(path_t), self.points)
        r = spline(t)

        return r.T

    def plot_path(self, p: np.array, h: np.array, t: float):
        field = Field()
        fig, ax = field.create_field()
        raw_positions = np.apply_along_axis(field.scale_down, 1, self.positions)
        p = np.apply_along_axis(field.scale_down, 1, p)

        # rx, ry = np.hsplit(raw_positions, 2)
        # f = self._interpolate(rx, ry, kind="linear")
        x, y = np.hsplit(p, 2)
        x_prime = [x[0]]
        y_prime = [y[0]]
        for i in range(1, h.shape[0]):
            x_prime.append(x[i - 1] + (self.speed * t * np.cos(h[i])))
            y_prime.append(y[i - 1] + (self.speed * t * np.sin(h[i])))
        ax.plot(p[:, 0], p[:, 1], "-", color="black")
        ax.plot(x_prime, y_prime, ':', color="green", markersize=2)
        ax.plot(raw_positions[:, 0], raw_positions[:, 1], "o", markersize=3, color="black")

        plt.title(f"Total time: {t:.2f} seconds", fontsize=7)
        ax.plot(*np.hsplit(p[0], 2), color="green", markersize=4)
        ax.plot(*np.hsplit(p[-1], 2), color="red", markersize=4)
        ax.annotate("Start", p[0], size=5, xytext=(p[0, 0], p[0, 1] + 40), )
        ax.annotate("End", p[-1], size=5, xytext=(p[-1, 0], p[-1, 1] + 40))

        ax.legend(['interpolated path', 'robot path', 'waypoints'], loc='best')
        file_name = "Map-%s.png"
        fig.savefig(f"paths/{self.path_name}/{next_path(file_name, f'paths/{self.path_name}/')}", dpi=300)

    def _print_distance(self, dist: float):
        """
Print distance of path
        :param dist: distance in feet
        """
        inch = round(feet_inch(dist), 2)
        feet = round(dist, 2)
        print(f"Distance (in): {-inch if self.negative_speed else inch}")
        print(f"Distance (ft): {-feet if self.negative_speed else feet}")

    def _interpolate_time(self, x, y):
        f3 = self._pchip_interpolator(x, y)
        dist = calculate_distance(f3)
        self._print_distance(dist)
        time = dist / self.speed
        counts = time / self.loop_time
        x_prime, y_prime = np.hsplit(f3, 2)
        x_prime, y_prime = x_prime.reshape(-1), y_prime.reshape(-1)
        dl = delta_distance(f3)
        l = np.cumsum(dl)
        ll = np.arange(start=0, stop=dist, step=dist / counts)
        assert l.shape == x_prime.shape and l.shape == y_prime.shape
        xx = interp1d(l, x_prime)
        yy = interp1d(l, y_prime)
        spaced_x = xx(ll)
        spaced_y = yy(ll)
        return np.column_stack([spaced_x, spaced_y]), time

    @staticmethod
    def prepend_inplace(xy1, xy2, xy3):
        points = np.array([xy1, xy2, xy3])
        heading = np.array(calculate_angle(points))
        wrapped_heading = wrap_angle(heading.item())
        inplace = np.array(wrapped_heading) / 0.02
        limit_degrees = 200
        counts = abs(int(math.ceil((inplace / math.radians(limit_degrees)))))
        turn = np.repeat(inplace / counts, counts)
        vel = np.repeat(0, turn.shape[0])
        return np.column_stack([vel.T, turn.T]), counts * 0.02,

    def export(self, plot=False, prepend=Optional[np.array], decelerate=False):
        x, y = np.hsplit(self.positions, 2)
        f3, time = self._interpolate_time(x, y)

        print(f"Total Time (seconds): {round(time, 2)}")
        h = calculate_heading(f3)
        delta_h = calculate_heading_rate(h, self.loop_time)
        self.plot_path(f3, h, time)
        if plot:
            plt.show()

        file_name = "Path-%s.txt"
        vel = np.repeat(-self.speed if self.negative_speed else self.speed, delta_h.shape[0])
        data = np.column_stack([vel, delta_h])
        if prepend is not None:
            # inplace, time = self._prepend_inplace(prepend, *f3[-2:])
            data = np.concatenate((prepend, np.zeros((3, 2)), data), axis=0)
        if decelerate:
            counts = int(self.decelerate_constant / (self.speed * self.loop_time))
            step = self.speed / counts
            vel = self.speed
            for i in range(-counts, 1, 1):
                if vel > self.speed:
                    data[i, 0] = 0
                    break
                data[i, 0] = -vel if self.negative_speed else vel
                vel -= step
        with open(f"paths/{self.path_name}/{next_path(file_name, f'paths/{self.path_name}/')}", "w") as f:
            for count in data:
                f.write(f"{count[0]:.4f},{count[1]:.4f}\n")


def calc_trajectory(pos, name, plot=True):
    for i, path in enumerate(pos):
        if path.inplace:
            points = np.array([pos[i - 1].data[-2], path.data[0], path.data[1]])
            heading = np.array(calculate_angle(points))
            wrapped_heading = wrap_angle(heading.item())
            inplace = np.array(wrapped_heading) / 0.02
            limit_degrees = 200
            # TODO limit turn speed to 150 deg/sec based off real data
            counts = abs(int(math.ceil((inplace / (limit_degrees * np.pi / 180)))))
            turn = np.repeat(inplace / counts, counts)
            vel = np.repeat(0, turn.shape[0])
            prepend = np.column_stack([vel.T, turn.T])
        else:
            prepend = None
        if len(path.data) < 2:
            continue
        print(f"\nPath {i}")
        print(f"Speed: {path.speed}")
        print(f"Inplace turn (rads): {round(wrapped_heading, 2) if prepend is not None else None}")
        t = Trajectory(path.to_numpy(), speed=path.speed, path_name=name)
        t.export(plot=plot, prepend=prepend, decelerate=path.decelerate)
