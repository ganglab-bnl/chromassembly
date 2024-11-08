from algorithm.Rotation import ScipyRotationDict
from algorithm.Voxel import Voxel
import copy
import numpy as np

class VoxelRotater:
    def __init__(self):
        self.scirot_dict = ScipyRotationDict()
        
    def rotate_voxel(self, voxel: Voxel, rot_label: str) -> Voxel:
        """
        Rotates a single voxel and returns a new Voxel object containing the new 
        rotated bonds. Used to compare bond colors in map_paint operations.
        """
        rot = self.scirot_dict.get_rotation(rot_label)
        new_voxel = copy.deepcopy(voxel)

        new_bonds = {}
        for direction, bond in new_voxel.bond_dict.dict.items():
            # Rotate the direction vector of the bond
            direction = np.array(direction)
            rotated_direction = tuple(np.round(rot(direction)).astype(int))

            old_bond = new_voxel.get_bond(direction)
            old_bond.direction = rotated_direction
            new_bonds[rotated_direction] = old_bond
        
        new_voxel.bond_dict.dict = new_bonds
        return new_voxel
        
    def rotate_voxel_bonds(self, voxel: Voxel, rot_label: str) -> dict[tuple[int, int, int], tuple[int, str]]:
        """
        Rotates a single voxel and returns a dictionary containing the rotated 
        directions as keys and the corresponding bond colors as values.
        
        Args:
            voxel (Voxel): The voxel to be rotated.
            rot_label (str): The rotation label to be applied.
            
        Returns:
            bond_dict (dict): A dictionary where keys are the rotated directions 
                              and values are tuples of (bond colors, bond types).
        """
        rot = self.scirot_dict.get_rotation(rot_label)
        
        bond_dict = {}
        for direction, bond in voxel.bond_dict.dict.items():
            # Rotate the direction vector of the bond
            direction = np.array(direction)
            rotated_direction = tuple(np.round(rot(direction)).astype(int))

            # Store the color in the bond_dict with the rotated direction as the key
            bond_dict[rotated_direction] = (bond.color, bond.type)
        
        return bond_dict
    

    def find_best_rotation(self, parent_voxel: Voxel, child_voxel: Voxel, rotations_to_check=None):
        """
        Find the best rotation which when applied to the parent_voxel, will
        minimize the difference between its bonds and the bonds of the child_voxel.
        """
        if rotations_to_check is None:
            rotations_to_check = list(self.scirot_dict.all_rotations.keys())
        
        best_rotation = None
        for rot_label in rotations_to_check:
            rot = self.scirot_dict.get_rotation(rot_label)
            # parent_bond_dict = {}
            
            found_valid_rotation = True
            for direction, parent_bond in parent_voxel.bond_dict.dict.items():
                direction = np.array(direction)
                rotated_direction = tuple(np.round(rot(direction)).astype(int))
                # parent_bond_dict[rotated_direction] = parent_bond.color
                if parent_bond.color == 0 or parent_bond.color is None:
                    continue
            
                # See if child_bond's color in that direction is (1) colored and if so, 
                # (2) matches parent_bond's color
                child_bond = child_voxel.get_bond(rotated_direction)
                if child_bond.color != 0 and child_bond.color is not None:
                    if child_bond.color != parent_bond.color:
                        found_valid_rotation = False
                        break

                # if child_bond.color != 0 and child_bond.color != parent_bond.color:
                #     # print(f"Child voxel{child_voxel.id} has a different color in direction {rotated_direction} after rotation {rot_label}")
                #     found_valid_rotation = False
                #     break

                # Ensure that result of coloring will not result in a palindromic voxel
                elif child_voxel.is_palindromic(parent_bond.color):
                    # print(f"Child voxel{child_voxel.id} is palindromic after rotation {rot_label}")
                    found_valid_rotation = False # child becomes palindromic
                    break
                elif child_bond.bond_partner.voxel.is_palindromic(-parent_bond.color):
                    # print(f"Child voxel{child_voxel.id}'s partner is palindromic after rotation {rot_label}")
                    found_valid_rotation = False # child's partner voxel becomes palindromic
                    break
            
            if found_valid_rotation:
                best_rotation = rot_label
                print(f"Found best rotation between voxel{parent_voxel.id} and voxel{child_voxel.id}: {best_rotation}")
                return best_rotation
            
        return best_rotation
    

    def compare_bond_dicts(parent_bond_dict: dict[tuple[int, int, int], int], 
                           child_bond_dict: dict[tuple[int, int, int], int]) -> bool:
        """
        Compares two bond dictionaries to see if a given rotation is a candidate for a swap_paint. 
        
        Args:
            bond_dict1 (dict): First bond dictionary {3D coordinates tuple: bond color (int)}
            bond_dict2 (dict): Second bond dictionary {3D coordinates tuple: bond color (int)}
        
        Returns:
            bool: True if the non-zero key-value pairs in common keys are equal, False otherwise.
        """
        # Get the common keys between the two dictionaries
        for direction, child_bond_color in child_bond_dict.items():
            
            if child_bond_color == 0: # Only need to check colored child bond equality
                continue

            parent_bond_color = parent_bond_dict[direction]
            if parent_bond_color != child_bond_color:
                return False
        
        # If all colored child_bonds are matched, return True
        return True

            