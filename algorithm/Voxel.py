import numpy as np
import logging
import copy
from .Bond import Bond

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
        self.bonds = {
            direction: Bond(voxel=self, direction=direction) for direction in self.vertex_directions
        }

    
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
            print(f" -> {self.get_direction_label(direction)}: {bond.color}, {bond.type}")
    
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

        Args:
            test_color (int): The color of the new bond we're considering to add
        """
        if test_color is None:
            return False
        
        for bond in self.bonds.values():
            if bond.color == -1*test_color:
                return True
        return False

    def get_bond_type(self, color: int) -> str:
        """
        Get the bond type for all bonds of the given color on the Voxel.
        Args:
            color (int): The color of the bond to search for

        Returns:
            bond_type (str): The bond type of all bonds on the voxel with the 
                             given color (None if not found)
        """
        for bond in self.bonds.values():
            if bond.color == color:
                return bond.type
        return None
    
    def is_equal_to(self, voxel2: 'Voxel') -> bool:
        """
        Check if two voxels are equal based on the colors of their bonds
        in the corresponding directions, and of course the material cargo.

        Args:
            voxel2 (Voxel): The second voxel to compare with
        """
        if self.material != voxel2.material:
            return False

        for direction in self.vertex_directions:
            if self.bonds[direction].color != voxel2.bonds[direction].color:
                return False

        return True
    
    def is_bond_equal_to(self, bond_dict: dict[tuple[int, int, int], int], comp_matters=True) -> bool:
        """
        Check if the bonds of the Voxel are equal to the given bond_dict.
        A faster version of is_equal_to, without deepcopying.
        Args:
            bond_dict (dict): A dictionary where keys are the bond directions 
                              and values are the bond colors
        """
        for direction, color in bond_dict.items():
            if not comp_matters:
                new_color = abs(color)
                old_color = abs(self.bonds[direction].color)
            else:
                new_color = color
                old_color = self.bonds[direction].color

            if old_color != new_color:
                return False
            
        return True
    
    def repaint_complement(self, color: int, complement: int) -> None:
        """
        Repaint the bonds of the given color to their complement.
        Args:
            color (int): The abs(color) of the bonds to repaint
        """
        for bond in self.bonds.values():
            if abs(bond.color) == color:
                bond.color = abs(bond.color)*complement
    
    def flip_complementarity(self, color: int, flipped_voxels=None) -> dict[int, int]:
        """
        Flip the complementarity of the bonds with the given color.
        
        Args:
            color (int): The abs(color) of the bonds to flip
        
        Returns:
            flipped_voxels (dict[int, int]): Dictionary of voxel IDs that would be flipped
                                            and their complementarity multipliers (+1 or -1)
        """
        if flipped_voxels is None:
            flipped_voxels = {}

        # Determine the current complementarity of the voxel
        current_complementarity = self.get_complementarity(color)
        if current_complementarity is None:
            raise ValueError(f"Voxel {self.id} does not have a bond with color {color}")
        
        # If this voxel is already flipped, skip it
        if self.id in flipped_voxels:
            return flipped_voxels

        # Register the flip for the current voxel
        flipped_voxels[self.id] = -current_complementarity  # Flip the complementarity

        for bond in self.bonds.values():
            if abs(bond.color) == color:
                partner_voxel = bond.bond_partner.voxel

                # Recursively flip the partner voxel if it hasn't been flipped already
                if partner_voxel.id not in flipped_voxels:
                    flipped_voxels = partner_voxel.flip_complementarity(color, flipped_voxels)

        return flipped_voxels


    
    def get_complementarity(self, color: int) -> int:
        """
        Get the complementarity of the bonds with the given color.
        Args:
            color (int): The abs(color) of the bonds to check
        Returns:
            complementarity (int): Whether the bond is the color (1) or its complement (-1)
        """
        for bond in self.bonds.values():
            if abs(bond.color) == abs(color):
                complementarity = bond.color // abs(bond.color)
                return complementarity
        # return complementarity

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

