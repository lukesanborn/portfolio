import numpy as np
import math


def calculate_angle(p: np.array) -> float:
    """
Calculate angle given three points
    :param p: np.array of 3 points
    :return: angle in radians
    """
    assert p.shape[0] == 3
    a = p[0]
    b = p[1]
    c = p[2]
    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    return angle if cosine_angle < 0 else -angle


def calculate_heading(p: np.array) -> np.array:
    x, y = np.hsplit(p, 2)
    x = x.reshape(-1)
    y = y.reshape(-1)
    diff_x = np.diff(x)
    diff_y = np.diff(y)
    assert diff_y.shape == diff_x.shape
    ac = np.arctan2(diff_y, diff_x)
    return ac


def wrap_angle(angle: float) -> float:
    if angle >= np.pi:
        angle -= 2 * np.pi
    elif angle < -np.pi:
        angle += 2 * np.pi
    return angle


def calculate_heading_rate(heading: np.array, loop_time: float = 0.02) -> np.array:
    heading_rate = np.insert(np.append(np.diff(heading), 0), 0, 0)
    fv = np.vectorize(wrap_angle)
    heading_rate_wrapped = fv(heading_rate)
    heading_delta = heading_rate_wrapped / loop_time
    return heading_delta
