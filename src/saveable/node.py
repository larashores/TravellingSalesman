from src.saveable.composite import Composite
from src.saveable.saveableInt import saveable_int
from src.saveable.saveableString import SaveableString


class Node(Composite):
    """
    Node type for travelling salesman problem. Holds integer x and y coordinates and the name of the node
    """
    x = saveable_int('u16')
    y = saveable_int('u16')
    name = SaveableString
