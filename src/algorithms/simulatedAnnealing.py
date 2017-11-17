import random
import math

import numpy as np
import warnings


def simulated_annealing(start_configuration, store_temperatures, temperatures):
    warnings.filterwarnings('error')
    lengths = np.zeros(len(temperatures))
    current = start_configuration
    for ind, temperature in enumerate(temperatures):
        if store_temperatures:
            lengths[ind] = current.value()
        change = current.get_successor_change()
        if change <= 0:
            current.next_successor()
        else:
            try:
                probability = math.e**(-change/temperature)
            except RuntimeWarning:
                probability = 0
            if random.random() <= probability:
                current.next_successor()
    print('Final value: {}'.format(start_configuration.value()))
    if store_temperatures:
        return lengths
