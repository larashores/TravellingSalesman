import numpy as np


def linear_temperature(start, num_steps):
    start /= 5
    interval = start / num_steps
    return np.arange(start, 0, -interval)


def decrease_ratio(start, ratio, num_steps):
    temps = [start]
    for _ in range(num_steps):
        temps.append(ratio*temps[-1])
    return temps
