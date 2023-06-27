from pprint import pprint

import numpy as np


def calculate_distance(xy: np.array) -> float:
    """
Calculate the total distance between many points in shape (x,2)
    :param xy: array of positions
    :return: total distance
    """
    return np.linalg.norm(np.diff(xy, axis=0), axis=1).sum()


def delta_distance(xy):
    dist = np.linalg.norm(np.diff(xy, axis=0), axis=1)
    dist = np.insert(dist, 0, 0, axis=0)
    return dist
