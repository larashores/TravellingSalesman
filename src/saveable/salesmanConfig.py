from src.saveable.composite import Composite
from src.saveable.saveableImage import SaveableImage
from src.saveable.saveableArray import array
from src.saveable.node import Node


class SalesmanConfig(Composite):
    """
    Represents the configuration of the salesman. Consists of a single background image and a list of nodes
    """
    background = SaveableImage
    nodes = array(Node)
