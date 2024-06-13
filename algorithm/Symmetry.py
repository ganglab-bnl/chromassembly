import numpy as np
from math import ceil, floor
from dataclasses import dataclass

from .Voxel import Voxel
from .Lattice import Lattice
from .Surroundings import SurroundingsManager

class SymmetryManager:
    def __init__(self, lattice: Lattice, SurroundingsManager: SurroundingsManager):
        """
        Manager class for performing symmetry operations on VoxelSurroundings
        """
        self.Lattice = lattice
        self.SurroundingsManager = SurroundingsManager
        self.SymmetryDict = {}

        self.single_rotations = {
            '90° Rotation in x axis': lambda x: np.rot90(x, 1, (1, 2)),
            '180° Rotation in x axis': lambda x: np.rot90(x, 2, (1, 2)),
            '270° Rotation in x axis': lambda x: np.rot90(x, 3, (1, 2)),
            '90° Rotation in y axis': lambda x: np.rot90(x, 1, (2, 0)),
            '180° Rotation in y axis': lambda x: np.rot90(x, 2, (2, 0)),
            '270° Rotation in y axis': lambda x: np.rot90(x, 3, (2, 0)),
            '90° Rotation in z axis': lambda x: np.rot90(x, 1, (0, 1)),
            '180° Rotation in z axis': lambda x: np.rot90(x, 2, (0, 1)),
            '270° Rotation in z axis': lambda x: np.rot90(x, 3, (0, 1))
        }
        self.reflections = {
            'Reflection in x-plane': lambda x: np.flip(x, 0),
            'Reflection in y-plane': lambda x: np.flip(x, 1),
            'Reflection in z-plane': lambda x: np.flip(x, 2)
        }
        # example usage
        # rotated_array = self.single_rotations['90° Rotation in x axis'](array)

    def hasSymmetry(self, voxel1: Voxel, voxel2: Voxel, symmetry: str):
        """
        Returns whether two voxels share a given symmetry.
        @param:
            - voxel1: Voxel object
            - voxel2: Voxel object
            - symmetry: string, the symmetry to check for
        @return:    
            - symmetry: Symmetry object
        """
        symmetry_function = self.single_rotations[symmetry]

        # Get the surroundings of each voxel (np slicing is a constant time operation)
        voxel1_surroundings = self.SurroundingsManager.getVoxelSurroundings(voxel1)
        voxel2_surroundings = self.SurroundingsManager.getVoxelSurroundings(voxel2)

        # Check if the surroundings of voxel1 are equal to the transformed surroundings of voxel2
        transformed_voxel1_surroundings = symmetry_function(voxel1_surroundings)
        if np.array_equal(transformed_voxel1_surroundings, voxel2_surroundings):
            return True # if so, return true!
        
        return False

@dataclass
class Symmetry:
    voxel1: Voxel
    voxel2: Voxel
    translation: list
    single_rotation: list
    double_rotation: list


if __name__ == '__main__':
    print("SymmetryManager tests:")