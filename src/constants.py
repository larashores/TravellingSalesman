import enum


class ChangeType(enum.Enum):
    """
    Constant used for Observables to notify observers that something has been changed or removed
    """
    ADD = 1
    REMOVE = 2
