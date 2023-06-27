import numpy as np
import pytest
from matplotlib import pyplot as plt

from src.ui.field import Field


class TestField:
    f = Field(54, 27, img_path="images/cropped_field.jpg")

    def test_field(self):
        fig, ax = self.f.create_field()
        _, xmax, ymin, _ = plt.axis()
        assert self.f.length / xmax == pytest.approx(self.f.width / ymin, 1e-2)

    def test_scale_up(self):
        p = np.array([500, 700])
        assert self.f.scale_up(p) == pytest.approx(np.array([12.7931, 17.9104]),0.1)

    def test_scale_down(self):
        p = np.array([28, 10])
        assert self.f.scale_down(p) == pytest.approx(np.array([1094.3333, 390.8333]),0.1)
