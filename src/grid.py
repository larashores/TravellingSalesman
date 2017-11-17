class Grid:
    """
    Makes a grid on top of another set of coordinates and allows for converting
    between them. The scale is how many units of the top coordinates are between
    each grid.
    """
    def __init__(self, scale):
        self.scale = scale

    def snap_to_grid(self, coordinates):
        """
        Purpose: Will return closest point on a grid that is overlaid on a larger
                 grid
        Inputs:
            coordinates: (x,y) pair of actual coordinates
        Output:
            (x,y) coordinates of the overlaid
        """
        x, y = coordinates[0], coordinates[1]
        left = x % self.scale
        top = y % self.scale
        right = self.scale - left
        bottom = self.scale - top
        if top < bottom:
            y = y - top
        else:
            y = y + bottom
        if left < right:
            x = x - left
        else:
            x = x - right
        return x, y

    def to_grid_coordinates(self, x, y):
        """
        Purpose: Converts actual coordinates to coordinates on the scaled grid
        Inputs:
            x:   x coordinate
            y:   y coordinate
        Output:
            Returns (x,y) coordinate pair
        """
        return x/self.scale, y/self.scale

    def from_grid_coordinates(self, x, y):
        """
        Purpose: Converts grid coordinates to scaled top coordinates
        Inputs:
            x:   x coordinate
            y:   y coordinate
        Output:
            Returns (x,y) coordinate pair
        """
        return x*self.scale, y*self.scale
