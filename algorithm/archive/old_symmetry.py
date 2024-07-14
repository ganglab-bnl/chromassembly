import numpy as np
import pandas as pd
from math import ceil, floor
from dataclasses import dataclass
from collections import defaultdict

from ..Voxel import Voxel
from .old_lattice import Lattice
from ..Surroundings import SurroundingsManager

class Symmetry:
    """
    Class storing all symmetries between two Voxels
    Attributes:
        voxelPair: frozenset of two voxels
        translation: bool
        single_rotations: dictionary of {"rotation": bool}
        double_rotations: dictionary of {"rotation": bool}
    """
    def __init__(self, voxelPair: frozenset):
        self.voxelPair = voxelPair
        self.translation = None  # bool, initialized as None
        self.single_rotations = {}
        self.double_rotations = {}
        self.reflections = {}
    
    def setSymmetry(self, trans_type: str, trans_label: str, result: bool):
        """
        Set the symmetry result for the voxel pair
        Example usage: 
            symmetry_obj.setSymmetry('single_rotations', '90° Rotation in X axis', True)
        """
        if trans_type == 'translation':
            self.translation = result
        elif trans_type == 'single_rotation':
            self.single_rotations[trans_label] = result
        elif trans_type == 'double_rotation':
            self.double_rotations[trans_label] = result
        elif trans_type == 'reflection':
            self.reflections[trans_label] = result
    
    def getSymmetry(self, trans_type: str, trans_label: str):
        """
        Get the symmetry result for the voxel pair
        Example usage:
            symmetry_obj.getSymmetry('single_rotations', '90° Rotation in X axis')
        """
        if trans_type == 'translation':
            return self.translation
        elif trans_type == 'single_rotation':
            return self.single_rotations.get(trans_label, None)
        elif trans_type == 'double_rotation':
            return self.double_rotations.get(trans_label, None)
    
    def hasAnySymmetry(self):
        """
        Check if the voxel pair shares any kind of symmetry at all.
        @return: bool
        """
        return any([self.translation, self.single_rotations, self.double_rotations, self.reflections])
    
    def getValidSymmetries(self):
        """
        Get the labels of all True symmetries for the voxel pair.
        """
        symmetries = []
        if self.translation:
            symmetries.append('Translation')
            
        # List comprehensions append only symmetries that are True
        symmetries += [sym for sym, isTrue in self.single_rotations.items() if isTrue]
        symmetries += [sym for sym, isTrue in self.double_rotations.items() if isTrue]
        symmetries += [sym for sym, isTrue in self.reflections.items() if isTrue]

        return symmetries

class SymmetryManager:
    def __init__(self, lattice: Lattice, SurroundingsManager: SurroundingsManager):
        """
        Manager class for performing symmetry operations on VoxelSurroundings
        """
        self.Lattice = lattice
        self.SurroundingsManager = SurroundingsManager
        self.SymmetryDict = self.initSymmetryDict()

        self.translation = {
            'translation': lambda x: x # Identity function
        }
        self.single_rotations = {
            '90° rotation in X axis': lambda x: np.rot90(x, 1, (0, 1)),
            '180° Rotation in X axis': lambda x: np.rot90(x, 2, (0, 1)),
            '270° Rotation in X axis': lambda x: np.rot90(x, 3, (0, 1)),
            '90° Rotation in Y axis': lambda x: np.rot90(x, 1, (0, 2)),  
            '180° Rotation in Y axis': lambda x: np.rot90(x, 2, (0, 2)),  
            '270° Rotation in Y axis': lambda x: np.rot90(x, 3, (0, 2)),  
            '90° Rotation in Z axis': lambda x: np.rot90(x, 1, (1, 2)),
            '180° Rotation in Z axis': lambda x: np.rot90(x, 2, (1, 2)),
            '270° Rotation in Z axis': lambda x: np.rot90(x, 3, (1, 2))
        }
        # Example usage:
        # rotated_array = self.single_rotations['90° Rotation in x axis'](array)

        self.double_rotations = self.initDoubleRotation_dict()

        self.reflections = { # Make an option to be able to consider reflections or not
            'Reflection in X plane': lambda x: np.flip(x, 0),
            'Reflection in Y plane': lambda x: np.flip(x, 1),
            'Reflection in Z plane': lambda x: np.flip(x, 2)
        }
        
        

    def initSymmetryDict(self):
        """
        Initialize self.SymmetryDict to have empty Symmetry objects for each voxel_pair combination
        """
        SymmetryDict = defaultdict(lambda: None)

        for voxel1 in self.Lattice.VoxelDict.values():
            for voxel2 in self.Lattice.VoxelDict.values():
                # The key to index dict and create Symmetry objects with
                voxel_pair = frozenset([voxel1, voxel2])
                # Initialize {voxel_pair, Symmetry} in SymmetryDict if not already present
                if voxel_pair not in SymmetryDict or SymmetryDict[voxel_pair] is None:
                    SymmetryDict[voxel_pair] = Symmetry(voxel_pair)

        return SymmetryDict
    
    def initDoubleRotation_dict(self):
        """
        Initialize double_rotations to contain all possible combinations of single_rotations,
        but excluding double rotations on the same axis.
        """
        double_rotations = {}
        for rotation1 in self.single_rotations.keys():
            for rotation2 in self.single_rotations.keys():
                # Get the second to last word in the string (the axis)
                rotation1_axis = rotation1.split(' ')[-2]
                rotation2_axis = rotation2.split(' ')[-2]
                # Only consider double rotation if they are on different axes
                if rotation1_axis != rotation2_axis:
                    double_rotations[f'{rotation1} + {rotation2}'] = lambda x: self.single_rotations[rotation2](self.single_rotations[rotation1](x))
        return double_rotations
    
    

    def checkAllSymmetries(self):
        """
        Check all symmetries for all pairs of voxels in the lattice.
        (Sorry it's a little hard to read now, will modularize later)
        """
        self.fillTransformations('translation')
        self.fillTransformations('single_rotation')
        self.fillTransformations('double_rotation')
    

    def fillTransformations(self, trans_type: str):
        """
        Fills Symmetry objects in SymmetryDict with booleans representing truthiness 
        of all transformations of a particular type, for all pairs of voxels in the lattice

        @param:
            - trans_type: the transformation type to check for, corresponding to either
              'translation', 'single_rotation' or 'double_rotation'
        @return: void
        """
        if trans_type == 'translation':
            transformations = self.translation
        elif trans_type == 'single_rotation':
            transformations = self.single_rotations
        elif trans_type == 'double_rotation':
            transformations = self.double_rotations
        
        for trans_label, trans_function in transformations.items():

            # Loop through all possible voxel pairs
            for voxel1 in self.Lattice.VoxelDict.values():

                # Transform surroundings of voxel1 once per symmetry
                voxel1_surroundings = self.SurroundingsManager.getVoxelSurroundings(voxel1)
                transformed_voxel1_surroundings = trans_function(voxel1_surroundings)

                for voxel2 in self.Lattice.VoxelDict.values():
                    # Make voxel pair to index into SymmetryDict
                    voxel_pair = frozenset([voxel1, voxel2])
                    symmetry_obj = self.SymmetryDict[voxel_pair] # Get symmetry object for the pair

                    # Skip if symmetry has already been checked
                    if symmetry_obj.getSymmetry(trans_type, trans_label) is not None:
                        continue

                    # Check symmetry:
                    # Two Voxels are symmetric if their surroundings are the same after one is transformed
                    voxel2_surroundings = self.SurroundingsManager.getVoxelSurroundings(voxel2)
                    has_symmetry = np.array_equal(transformed_voxel1_surroundings, voxel2_surroundings) 

                    symmetry_obj.setSymmetry(trans_type, trans_label, has_symmetry) # Append result to symmetry object
                    self.SymmetryDict[voxel_pair] = symmetry_obj # Add to SymmetryDict


    def makeSymmetryDf(self):
        """
        Create a DataFrame from the SymmetryDict (for debugging)
        """
        columns = ['Voxel Pair'] + list(self.translation.keys()) + list(self.single_rotations.keys()) + list(self.double_rotations.keys())
        symmetry_df = []
        trans_types = ['translation', 'single_rotation', 'double_rotation']

        for voxel_pair, symmetry_obj in self.SymmetryDict.items():
            # Generate a tuple of voxel indices
            indices_tuple = tuple(voxel.index for voxel in voxel_pair)
            row = [indices_tuple]

            row.append(symmetry_obj.translation) # Append translation result (bool)

            for sym in self.single_rotations.keys():
                # Fetch the result using the dictionary
                result = symmetry_obj.single_rotations.get(sym, 'hi')  # Default to None if not found
                row.append(result)
            
            for sym in self.double_rotations.keys():
                result = symmetry_obj.double_rotations.get(sym, 'hi')
                row.append(result)

            symmetry_df.append(row)

        # Create DataFrame from collected data
        SymmetryDf = pd.DataFrame(symmetry_df, columns=columns)
        return SymmetryDf



if __name__ == '__main__':
    # Doesn't work yet because of import voodoo :( sorry
    print("SymmetryManager tests\n---\n")

    input_lattice = np.load('lattice.npy')
    print(f'Input lattice:\n{input_lattice}\n')

    lattice = Lattice(input_lattice)
    print(f'Min design:\n{lattice.MinDesign}\n')
    print(f'Voxels:\n{lattice.VoxelDict}\n')
    print(f'Voxel indices:\n{[voxel.index for voxel in lattice.VoxelDict.values()]}\n')

    surr_manager = SurroundingsManager(lattice)
    print(f'Full surroundings:\n{surr_manager.FullSurroundings}\n')
    # print(f'VoxelSurroundings for voxel 0:\n{surr_manager.getVoxelSurroundings(lattice.voxels[0])}\n')
    # print(f'VoxelSurroundings for voxel 1:\n{surr_manager.getVoxelSurroundings(lattice.voxels[1])}\n')

    sym_manager = SymmetryManager(lattice, surr_manager)
    sym_manager.checkAllSymmetries()
    print(f'SymmetryDict:\n{sym_manager.SymmetryDict}\n')

