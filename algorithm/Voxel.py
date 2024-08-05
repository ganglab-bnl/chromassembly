import numpy as np
from .Bond import Bond
import logging

class Voxel:
    """
    The 'Voxel' represents the octahedral DNA origami, to be tiled in
    the 3D Lattice structure. It contains a material cargo (int) and 
    6 Bonds attached to each vertex. 

    Methods:
        - get_bond(direction): Get the bond in a given direction
        - get_partner(direction): Returns partner Bond + Voxel objects 
                                  in the supplied direction
    """
    def __init__(self, id: int, material: int, coordinates: tuple[float, float, float],
                 np_index: tuple[int, int, int]):
        """
        Initialize a Voxel object with a unique ID, material, and coordinates.
        @param:
            - id: the unique identifier for the Voxel
            - material: the material cargo of the Voxel
            - coordinates: the Voxel's coordinates in the Lattice.MinDesign
            - np_index: The 'material' value's index into the MinDesign np.array
        """
        self.id = id
        self.material = material
        self.coordinates = coordinates
        self.np_index = np_index

        # ----- Vertex information ----- #
        # Vertex positions for octahedral structures
        self.vertex_names = [
            "+x", "-x", 
            "+y", "-y", 
            "+z", "-z"
        ]
        # Vector (euclidean) representing direction of each vertex 
        # wrt. the Voxel @ (0,0,0)
        self.vertex_directions = [
            (1, 0, 0), (-1, 0, 0),   # +-x
            (0, 1, 0), (0, -1, 0),   # +-y
            (0, 0, 1), (0, 0, -1)    # +-z
        ]
        # Initialize bond for each vertex
        self.bonds = {direction: Bond(voxel=self, direction=direction) for direction in self.vertex_directions}

    
    # --- Public methods --- #
    def get_bond(self, direction) -> Bond:
        """
        Get the bond in a given direction. Accepts '+x', '-y', etc. or 
        a tuple/np.array representing the vector direction of the bond wrt. the
        Voxel @ (0, 0, 0)
        """
        direction = self._handle_direction(direction)
        return self.bonds.get(direction)
    
    def get_partner(self, direction) -> tuple['Voxel', Bond]:
        """
        Get the partner Voxel + Bond objects in the supplied direction.
        (Direction can be str, tuple, or np.ndarray)
        """
        bond = self.get_bond(direction)
        bond_partner = bond.bond_partner

        if bond_partner is None:
            logging.error(f"No bond partner found for Voxel {self.id} in direction {direction}")
            return None, None

        voxel_partner = bond_partner.voxel
        return voxel_partner, bond_partner
    
    def has_bond_partner_with(self, partner_voxel: 'Voxel'):
        """If the voxel has a bond partner with the supplied Voxel object,
        return the current Voxel's bond object which has the partner with the
        partner_voxel."""

        for bond in self.bonds.values():
            if bond.bond_partner is None:
                continue
            if bond.bond_partner.voxel == partner_voxel:
                return bond
            
        return None
    
    def print_bonds(self) -> None:
        """Print all bonds of the Voxel."""
        print(f"Voxel {self.id} ({self.material}):\n---")
        for direction, bond in self.bonds.items():
            print(f" -> {self.get_direction_label(direction)}: {bond.color}")
    
    def get_direction_label(self, direction):
        """
        Get the label of the direction (ex: '+x', '-y', etc.)
        """
        direction = self._handle_direction(direction)
        direction_index = self.vertex_directions.index(direction)
        return self.vertex_names[direction_index]
    
    def is_palindromic(self, test_color: int) -> bool:
        """
        Check if adding a new bond color will create a palindromic structure.
        """
        for bond in self.bonds.values():
            if bond.color == -1*test_color:
                return True
        return False

    # --- Internal methods --- #
    def _handle_direction(self, direction):
        """
        Formats any kind of 'direction' input into a tuple.
        Handles:
            - str: "+x", "-y", ...
            - np.array: np.array([1, 0, 0]), ...
            - tuple: (1, 0, 0), ...
        """
        if isinstance(direction, str): 
            # Case 1: direction is a str "+x", "-y", ...
            direction_index = self.vertex_names.index(direction)
            direction = self.vertex_directions[direction_index]

        elif isinstance(direction, np.ndarray): 
            # Case 2: direction is a np.array([1, 0, 0]), ...
            direction = tuple(direction)
        
        return direction # Now direction is a tuple :-)

