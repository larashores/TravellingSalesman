import enum
import numpy as np
import random

from src.constants import ChangeType
from src.observable import Observable


class SuccessorChooseType(enum.Enum):
    BOTH_RANDOM = 0
    RANDOM_NEIGHBORS = 1


class PathState(Observable):
    """
    Keeps track of the state of 1 configuration of the travelling salseman problem

    Attributes:
        nodes: The nodes that are a part of the current path in order
        weights: A dictionary of weights that are indexed by a frozenset of two different nodes (weights are equal both
            ways across an edge
        current_value: Stores the current value of the array so it can simply be looked up instead of recalculated
        self.next_start_ind: The start index of the next path range to flip
        self.next_end_ind: The end index of the next path range to flip
    """
    def __init__(self, weights, successor_choose_type, notify_canvas):
        Observable.__init__(self)
        self.nodes = []
        self.weights = weights
        self.current_value = None
        self.notify_canvas = notify_canvas
        self.next_start_ind = 0
        self.next_end_ind = 0
        self.next_change = 0

        if successor_choose_type == SuccessorChooseType.BOTH_RANDOM:
            self.generate_next_indices = self.generate_two_random_indices
        elif successor_choose_type == SuccessorChooseType.RANDOM_NEIGHBORS:
            self.generate_next_indices = self.generate_random_neighboring_indices

    def generate_two_random_indices(self):
        """
        Generates the next indices to flip randomly. Ignores the first and last indices and will not pick the same
        index. Stores the results in self.next_start_ind, self.next_end_ind
        """
        # Ignore the edges of the graph
        rand1 = int(random.random() * (len(self.nodes)-2)) + 1
        while True:
            rand2 = int(random.random() * (len(self.nodes)-2)) + 1
            if rand2 != rand1:
                self.next_start_ind = min(rand1, rand2)
                self.next_end_ind = max(rand1, rand2)
                return

    def generate_random_neighboring_indices(self):
        """
        Generates the next indices to flip randomly. Ignores the first and last indices and will not pick the same
        index. Stores the results in self.next_start_ind, self.next_end_ind
        """
        # Ignore the edges of the graph
        rand1 = int(random.random() * (len(self.nodes)-2)) + 1
        rand2 = rand1 - 1 if rand1 != 1 else rand1 + 1
        self.next_start_ind = min(rand1, rand2)
        self.next_end_ind = max(rand1, rand2)

    def value(self):
        """
        Gets the current value of the path which is simply it's total weight. Caches the value

        Returns:
            The total weight
        """
        if self.current_value:
            return self.current_value
        total_weight = 0
        for i, node1 in enumerate(self.nodes):
            node2 = self.nodes[(i+1) % len(self.nodes)]
            total_weight += self.weights[frozenset([node1, node2])]
        self.current_value = total_weight
        return total_weight

    def get_successor_change(self):
        """
        Gets the change in weight that would happen if the two indices that are ready to flip were flipped. Only
        calculates the changed weights instead of the entire path for faster calculation
        """
        self.generate_next_indices()
        start, end = self.next_start_ind, self.next_end_ind
        old_weights = 0
        old_weights += self.weight_between_indices(start, start-1)
        old_weights += self.weight_between_indices(end, end+1)

        new_weights = 0
        new_weights += self.weight_between_indices(end, start-1)
        new_weights += self.weight_between_indices(start, end+1)
        self.next_change = new_weights - old_weights
        return self.next_change

    def weight_between_indices(self, index1, index2):
        """
        Returns the weight between two nodes given their indices in the list of nodes

        Args:
            index1: The index of the first node
            index2: The index of the second node

        Returns:
            The weight between the two nodes
        """
        return self.weights[frozenset((self.nodes[index1], self.nodes[index2]))]

    def notify(self, change_type, index1, index2):
        """
        Notifies all observers that an edges was either added or deleted from the path

        Args:
            change_type: Whether the edge was added or deleted
            index1: The index of the first node in the edge
            index2: The index of the second node in the edge
        """
        self.notify_observers(change_type, self.nodes[index1], self.nodes[index2])

    def next_successor(self):
        """
        Using the values calculated in get_successor_change, edits the configuration by flipping the subpath between
        those two nodes
        """
        if self.notify_canvas:
            self.notify(ChangeType.REMOVE, self.next_start_ind-1, self.next_start_ind)
            self.notify(ChangeType.REMOVE, self.next_end_ind, self.next_end_ind+1)
        self.nodes[self.next_start_ind:self.next_end_ind+1] = \
            reversed(self.nodes[self.next_start_ind:self.next_end_ind+1])
        self.current_value = self.value() + self.next_change
        if self.notify_canvas:
            self.notify(ChangeType.ADD, self.next_start_ind-1, self.next_start_ind)
            self.notify(ChangeType.ADD, self.next_end_ind, self.next_end_ind+1)


class SimulatedAnnealingModel(Observable):
    """
    Simple class to generate and initial PathState. This class will can be observed and it will pass all observes on two
    the path state. notify_observers(ChangeType, node1, node2) will be called whenever an edge is added or deleted
    """
    def __init__(self):
        Observable.__init__(self)
        self.nodes = []
        self.weights = {}

    def init(self):
        """
        Initializes the weights for the nodes. Called before generating a start state
        """
        nodes = self.nodes
        num_nodes = len(nodes)
        for i, j in np.ndindex((num_nodes, num_nodes)):
            point1 = np.array([nodes[i].x, nodes[i].y])
            point2 = np.array([nodes[j].x, nodes[j].y])
            self.weights[frozenset([nodes[i], nodes[j]])] = np.linalg.norm(point1-point2)

    def start_state(self, successor_choose_type, notify_canvas=True):
        """
        Gets a start PathState to run a simulation on
        """
        self.init()
        state = PathState(self.weights, successor_choose_type, notify_canvas)
        state.nodes.append(self.nodes[0])
        for ind in range(1, len(self.nodes)):
            state.nodes.append(self.nodes[ind])
            if notify_canvas:
                self.notify_observers(ChangeType.ADD, self.nodes[ind-1], self.nodes[ind])
        state.nodes.append(self.nodes[0])
        state.observers.update(self.observers)
        if notify_canvas:
            self.notify_observers(ChangeType.ADD, self.nodes[len(self.nodes)-1], self.nodes[0])
        state.generate_next_indices()
        return state
