import numpy as np

from algorithm.data_structures.PointGroup import PointGroup

class Voxel:
    """
    The 'Voxel' is the wrapper around the PointGroup which handles the
    ways in which the individual PointGroup must interact within the DNA
    lattice structure. 

    Notable methods:
        - get_bond(direction): Get the bond in a given direction
        - get_partner(direction): Returns partner Bond + Voxel
    """
    def __init__(self, id: int, cargo: int, coordinates: tuple[float, float, float],
                 np_index: tuple[int, int, int]):
        """
        Initialize a Voxel object with a unique ID, material, and coordinates.
        @param:
            - id (int): the unique identifier for the Voxel
            - cargo (int): the material cargo of the Voxel 
            - coordinates: the Voxel's coordinates in the Lattice.MinDesign
            - np_index: The 'material' value's index into the MinDesign np.array
        """
        self.id = id
        self.cargo = cargo
        self.coordinates = coordinates
        self.np_index = np_index

        # Initialize the point group to store all structurally identifying data
        # e.g., bond colors and material cargo
        self.point_group = PointGroup(geometry="octahedron")
        self.point_group.set_point('cargo', cargo) # init only with cargo (bonds colored by algo later)

        # Copy the same point names and point directions as the point_group
        # In the Voxel, we call them "vertices"
        self.vertex_names = getattr(self.point_group, 'point_names')
        self.vertex_directions = getattr(self.point_group, 'point_directions')

        # We will store the neighbors (which share a 'partner' bond with this voxel)
        # in a separate dictionary to not muddle up the point group with unnecessary info
        # (saves computation time)
        self.partners = {direction: None for direction in self.vertex_directions}

    # --- PUBLIC METHODS --- #
    def get_bond(self, direction):
        """
        Returns the bond (aka the Point representing this bond) in the 
        supplied direction. Enables Painter to manipulate the Point's 'data' 
        attribute - e.g., to 'color' the bond.
        """
        return self.point_group.get_point(direction)
    
    def set_partner(self, direction):
        """
        Set the partner voxel / bond (Point) in the specified direction
        """

    # --- 