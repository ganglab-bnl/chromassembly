import numpy as np
import pandas as pd
from math import ceil, floor
from dataclasses import dataclass
from collections import defaultdict

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
        self.SymmetryDict = self.initSymmetryDict()

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

    def initSymmetryDict(self):
        """
        Initialize self.SymmetryDict to have empty Symmetry objects for each voxel_pair combination
        """
        SymmetryDict = defaultdict(lambda: None)

        for voxel1 in self.Lattice.voxels:
            for voxel2 in self.Lattice.voxels:
                # The key to index dict and create Symmetry objects with
                voxel_pair = frozenset([voxel1, voxel2])
                # Initialize {voxel_pair, Symmetry} in SymmetryDict if not already present
                if voxel_pair not in SymmetryDict or SymmetryDict[voxel_pair] is None:
                    SymmetryDict[voxel_pair] = Symmetry(voxel_pair)

        return SymmetryDict
    
    def hasSymmetry(self, transformed_voxel1_surroundings: np.array, voxel2: Voxel):
        """
        Returns whether two voxels share a given symmetry.
        (Accepts transformed_voxel1_surroundings to avoid repeating transformation computation)
        @param:
            - transformed_voxel1_surroundings: np.array, the surroundings of voxel1 after a symmetry transformation
            - voxel2: Voxel object
        @return:
            - bool, true or false
        """
        # Return True if surroundings np.arrays are equal, else False
        voxel2_surroundings = self.SurroundingsManager.getVoxelSurroundings(voxel2)
        if np.array_equal(transformed_voxel1_surroundings, voxel2_surroundings):
            return True
        return False

    def checkAllSymmetries(self):
        """
        Check all symmetries for all pairs of voxels in the lattice.
        (Sorry it's a little hard to read now, will modularize later)
        """
        for symmetry in self.single_rotations.keys():
            # Loop through all possible voxel pairs
            for voxel1 in self.Lattice.voxels:
                # Transform surroundings of voxel1 once per symmetry, (slight computational efficiency)
                # for all possible voxel1's in voxels[]
                voxel1_surroundings = self.SurroundingsManager.getVoxelSurroundings(voxel1)
                transformed_voxel1_surroundings = self.single_rotations[symmetry](voxel1_surroundings)

                for voxel2 in self.Lattice.voxels:

                    voxel_pair = frozenset([voxel1, voxel2])
                    voxel_pair_symmetry = self.SymmetryDict[voxel_pair]

                    has_symmetry = self.hasSymmetry(transformed_voxel1_surroundings, voxel2) # bool
                    voxel_pair_symmetry.single_rotations[symmetry] = has_symmetry

                    self.SymmetryDict[voxel_pair] = voxel_pair_symmetry

    def getSymmetryDict_df(self):
        """
        Create a DataFrame from the SymmetryDict (for debugging)
        """
        columns = ['Voxel Pair'] + list(self.single_rotations.keys())
        data = []

        for voxel_pair, symmetry_obj in self.SymmetryDict.items():
            # Generate a tuple of voxel indices
            indices_tuple = tuple(voxel.index for voxel in voxel_pair)
            row = [indices_tuple]

            for sym in self.single_rotations.keys():
                # Fetch the result using the dictionary
                result = symmetry_obj.single_rotations.get(sym, False)  # Default to False if not found
                row.append(result)

            data.append(row)

        # Create DataFrame from collected data
        df = pd.DataFrame(data, columns=columns)
        return df

class Symmetry:
    def __init__(self, voxelPair: frozenset):
        self.voxelPair = voxelPair
        self.translations = []
        self.single_rotations = {}
        self.double_rotations = []


if __name__ == '__main__':
    # Doesn't work yet because of import voodoo :( sorry
    print("SymmetryManager tests\n---\n")

    input_lattice = np.load('lattice.npy')
    print(f'Input lattice:\n{input_lattice}\n')

    lattice = Lattice(input_lattice)
    print(f'Min design:\n{lattice.MinDesign}\n')
    print(f'Voxels:\n{lattice.voxels}\n')
    print(f'Voxel indices:\n{[voxel.index for voxel in lattice.voxels]}\n')

    surr_manager = SurroundingsManager(lattice)
    print(f'Full surroundings:\n{surr_manager.FullSurroundings}\n')
    print(f'VoxelSurroundings for voxel 0:\n{surr_manager.getVoxelSurroundings(lattice.voxels[0])}\n')
    print(f'VoxelSurroundings for voxel 1:\n{surr_manager.getVoxelSurroundings(lattice.voxels[1])}\n')

    sym_manager = SymmetryManager(lattice, surr_manager)
    sym_manager.checkAllSymmetries()
    print(f'SymmetryDict:\n{sym_manager.SymmetryDict}\n')
