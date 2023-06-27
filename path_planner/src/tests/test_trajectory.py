import numpy as np
import pytest
from matplotlib import pyplot as plt

from src.trajectory import Trajectory
from src.utils import calculate_angle, calculate_heading


class TestTrajectory:
    positions = np.array([[1, 1], [4, 5], [7, 1]])
    def test_left_traj(self):
        positions = self.positions[::-1]
        self.interpolate(positions)

    def test_right_traj(self):
        self.interpolate(self.positions)

    def test_right_angle(self):

        angle = calculate_heading(self.positions)
        assert True

    def test_left_angle(self):
        positions = self.positions[::-1]
        angle = calculate_heading(positions)
        assert True
    def interpolate(self,positions):
        x, y = np.hsplit(positions, 2)
        plt.plot(x, y)
        t = Trajectory(positions, points=100)
        f3 = t._pchip_interpolator(x, y)
        plt.plot(f3[:, 0], f3[:, 1])
        f4, _ = t._interpolate_time(x, y)
        print(f4)
        plt.plot(f4[:, 0], f4[:, 1])
        plt.legend(['raw', 'pchip', 'time interpolate'])
        plt.show()
