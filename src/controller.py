import enum
from PIL import Image
from src.algorithms.simulatedAnnealing import simulated_annealing
from src.graphing.graphing import draw
from src.graphing.graph import Graph
from src.graphing.subplot import SubPlot
from src.observable import Observable
from src.saveable.salesmanConfig import SalesmanConfig
from src.saveable.node import Node
from src.runtime_models.simulatedAnnealingModel import SimulatedAnnealingModel



class RunStatus(enum.Enum):
    """
    Enum used to indicate that the algorithm is being solved or is done solving
    """
    START = 0
    END = 1


def load_image(name):
    """
    Opens an image file from a path and returns it
    """
    with open(name, 'rb') as file:
        image = Image.open(file)
        image.load()
        return image


class Controller(Observable):
    """
    Controller used for the GUI to perform some non-trivial functions
    """
    def __init__(self):
        Observable.__init__(self)
        self.model = SalesmanConfig()               # The model that contains all of the save able configuration data
        self.annealing = SimulatedAnnealingModel()  # A model that contains all of the runtime information
        self.max_dist_func = lambda: 1           # Function that is used to determine the maximum possible path distance
        self.get_successor_type = lambda: None

    def save(self, path):
        """
        Saves the model to a file path

        Args:
            path: The path to save to
        """
        data = self.model.to_byte_array()
        file = open(path, 'wb')
        file.write(data)
        file.close()

    def load(self, path):
        """
        Loads the model from a file path

        Args:
            path: The path to load from
        """
        file = open(path, 'rb')
        array = bytearray(file.read())
        self.model.load_in_place(array)

    def new(self, name):
        """
        Given the name of an image path, loads the image into the model and clears all nodes

        Args:
            name: Name of the image file to load
        """
        img = load_image(name)
        self.model.background = img
        self.model.nodes.clear()

    def create_node(self, x, y):
        """
        Creates a new node given a pair of coordinates and adds it to the model

        Args:
            x: The x-coordinate
            y: The y-coordinate
        """
        node = Node()
        node.x = x
        node.y = y
        node.name = 'Node'
        self.model.nodes.append(node)

    def delete_node(self, node):
        """
        Deletes a node from the model

        Args:
            node: The node to delete
        """
        self.model.nodes.remove(node)

    def run(self, temperatures, *, generate_graphs=False, track_lengths=False, graph_scale=None, notify_canvas=True):
        """
        Given a list of temperatures, runs the simulation
        """
        self.annealing.nodes = self.model.nodes.values[:]
        self.notify_observers(RunStatus.START)
        start_state = self.annealing.start_state(self.get_successor_type(), notify_canvas)
        lengths = simulated_annealing(start_state, track_lengths or generate_graphs, temperatures)
        if generate_graphs:
            graphs = [[SubPlot(Graph(list(range(len(temperatures))), lengths, plot_type='-'),
                               title='Path Length at each Step',
                               x_label='Step', y_label='Total Path Length'),
                       SubPlot(Graph(list(range(len(temperatures))), temperatures, plot_type='-'),
                               title='Temperature at each Step',
                               x_label='Step', y_label='Temperature',
                               log=graph_scale)]]
            draw(graphs)
        self.notify_observers(RunStatus.END)
        return start_state.value(), lengths


