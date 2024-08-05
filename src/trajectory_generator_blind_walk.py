import numpy as np


def compute_pos_hip(time):
    return np.sin(time)


def compute_pos_knee(time):
    return np.cos(time)
