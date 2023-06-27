import numpy as np

from src.utils import calculate_distance, delta_distance


def test_distance():
    positions = np.array([[1, 1], [4, 5], [7, 1]])
    dist1 = delta_distance(positions)
    dist2 = calculate_distance(positions)
    assert dist1.sum() == dist2


def test_inverse_distance():
    positions = np.array([[1, 1], [4, 5], [7, 1]])
    positions = positions[::-1]
    dist1 = delta_distance(positions)
    dist2 = calculate_distance(positions)
    assert dist1.sum() == dist2
