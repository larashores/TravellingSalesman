class Observable:
    """
    Observer class that allows a function to register with the class. The class can notify all observers with any
    arguments
    """

    def __init__(self):
        """
        Sets up the set of all observer functions
        """
        self.__dict__['observers'] = set()  # Use __dict__ as this was causing conflicts with Composite

    def register(self, observer):
        """
        Adds a callable object to the set of observers

        Args:
            observer: The callable to add
        """
        self.observers.add(observer)

    def unregister(self, observer):
        """
        Removes a callable object from the set of observers

        Args:
            observer: The callable to remove
        """
        if observer in self.observers:
            self.observers.remove(observer)

    def unregister_all(self):
        """
        Removes all observers from the class
        """
        self.observers.clear()

    def notify_observers(self, *args, **kwargs):
        """
        Notifies all observers with any amount of arguments

        Args:
            args: Arbitrary positional arguments
            kwargs: Arbitrary keyword arguments
        """
        for observer in self.observers:
            observer(*args, **kwargs)
