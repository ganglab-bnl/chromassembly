import numpy as np
import pandas as pd

from .Voxel import Voxel
from .Lattice import Lattice
from .Surroundings import SurroundingsManager

class SymmetryDf:
    """
    Class which stores all combinations of voxel pairs and their symmetries.
    """
    def __init__(self, lattice: Lattice, SurroundingsManager: SurroundingsManager):
        """
        Initialize the SymmetryDf object.
        """
        self.Lattice = lattice
        self.SurroundingsManager = SurroundingsManager
        # self.SymmetryDf = self.initSymmetryDf()

        # Initialize dictionaries for transformation functions
        self.translation = {
            'translation': lambda x: x # Identity function
        }
        self.single_rotations = {
            '90° X-axis': lambda x: np.rot90(x, 1, (0, 1)),
            '180° X-axis': lambda x: np.rot90(x, 2, (0, 1)),
            '270° X-axis': lambda x: np.rot90(x, 3, (0, 1)),
            '90° Y-axis': lambda x: np.rot90(x, 1, (0, 2)),  
            '180° Y-axis': lambda x: np.rot90(x, 2, (0, 2)),  
            '270° Y-axis': lambda x: np.rot90(x, 3, (0, 2)),  
            '90° Z-axis': lambda x: np.rot90(x, 1, (1, 2)),
            '180° Z-axis': lambda x: np.rot90(x, 2, (1, 2)),
            '270° Z-axis': lambda x: np.rot90(x, 3, (1, 2))
        }
        self.double_rotations = self.init_double_rotations()

        # Initialize dictionary of all possible symmetry operations
        self.symmetry_operations = {**self.translation, **self.single_rotations, **self.double_rotations}
        
        # Initialize symmetry_df
        self.symmetry_df = self.init_symmetry_df()


    @staticmethod
    def convert_frozenset_to_str(voxel_pair: frozenset):
        """
        Convert a frozenset to a string
        E.g., "frozenset({0, 1})" -> "(0, 1)"
        @param:
            - voxel_pair: a frozenset of two voxel.indices
        @return:
            - string: str, frozenset({0, 1})
        """
        # Convert each integer in the frozenset to a string, then sort and join
        frozen_str = "(" + ", ".join(map(str, voxel_pair)) + ")"
        return frozen_str

    
    def init_double_rotations(self):
        """
        Initialize double_rotations to contain all possible combinations of single_rotations,
        but excluding double rotations on the same axis.
        @return:
            - double_rotations: Dictionary of lambda functions for double rotations
                                {"rotation1 + rotation2": lambda x: rotation2(rotation1(x))}
        """
        frozen_double_rotations = []
        for rotation1 in self.single_rotations.keys():
            for rotation2 in self.single_rotations.keys():
                # Create a frozen set of the pair of rotations
                rotation_pair = frozenset([rotation1, rotation2])
                rotation1_axis = rotation1.split(' ')[-1] # Last word in string (the axis)
                rotation2_axis = rotation2.split(' ')[-1]

                # Only consider double rotation if they are on different axes and not already considered
                if rotation1_axis != rotation2_axis and rotation_pair not in frozen_double_rotations:
                    frozen_double_rotations.append(rotation_pair)
        
        # Iterate through list of non-repeating double rotations and create a dictionary of lambda functions
        double_rotations = {}
        for rotation_pair in frozen_double_rotations:
            rotation1, rotation2 = rotation_pair
            double_rotations[f'{rotation1} + {rotation2}'] = lambda x: self.single_rotations[rotation2](self.single_rotations[rotation1](x))
        
        # Sort the dictionary by key
        sorted_double_rotations = {key: double_rotations[key] for key in sorted(double_rotations)}

        return sorted_double_rotations


    def init_symmetry_df(self):
        """
        Initialize an empty symmetry_df with all possible voxel pairs and symmetry operations
        to be filled later.
        @return:
            - symmetry_df: Pandas DataFrame object
        """
        # Create a list of all possible voxel pairs
        voxel_pairs_set = set()
        for voxel1 in self.Lattice.VoxelDict.values():
            for voxel2 in self.Lattice.VoxelDict.values():
                voxel_pairs_set.add(frozenset([voxel1.index, voxel2.index]))
        
        voxel_pairs = [self.convert_frozenset_to_str(pair) for pair in sorted(voxel_pairs_set)]

        # Create a dataframe containing True or False for each symmetry operation as the column names
        symmetry_df = pd.DataFrame(index=voxel_pairs, columns=self.symmetry_operations.keys())
        # symmetry_df = symmetry_df.fillna(None) # Fill NaN values with None

        return symmetry_df
    
    
    def compute_all_symmetries(self):
        """
        Compute all possible symmetries between two voxels.
        @param:
            - voxel1: Voxel object
            - voxel2: Voxel object
        @return:
            - symmetries: Dictionary of symmetries between voxel1 and voxel2
        """
        symmetries = {}
        for sym_label, sym_function in self.symmetry_operations.items():

            # Loop through all possible voxel pairs
            for voxel1 in self.Lattice.VoxelDict.values():

                # Transform surroundings of voxel1 once per symmetry
                voxel1_surroundings = self.SurroundingsManager.getVoxelSurroundings(voxel1)
                transformed_voxel1_surroundings = sym_function(voxel1_surroundings)

                for voxel2 in self.Lattice.VoxelDict.values():
                    # Make voxel pair to index into SymmetryDict
                    voxel_pair = frozenset([voxel1.index, voxel2.index])
                    voxel_pair_index = self.convert_frozenset_to_str(voxel_pair) # index with str

                    # print(f'Checking symmetry for {voxel_pair_index} with {sym_label}...') # debug
    
                    symmetry_already_computed = not pd.isna(self.symmetry_df.loc[voxel_pair_index, sym_label])

                    if symmetry_already_computed:
                        continue # Symmetry already exists in symmetry_df

                    # Check symmetry:
                    # Two Voxels are symmetric if their surroundings are the same after one is transformed
                    voxel2_surroundings = self.SurroundingsManager.getVoxelSurroundings(voxel2)
                    has_symmetry = np.array_equal(transformed_voxel1_surroundings, voxel2_surroundings) 

                    self.symmetry_df.loc[voxel_pair_index, sym_label] = has_symmetry # Store the result in symmetry_df

    def symlist(self, voxel_pair: frozenset):
        """
        Get the list of symmetries for a specific voxel pair
        """
        voxel_pair_index = self.convert_frozenset_to_str(voxel_pair)
        all_symmetries = self.symmetry_df.loc[voxel_pair_index]
        valid_symmetries = all_symmetries[all_symmetries == True].index
        symlist = list(valid_symmetries)
        return symlist
    
    def symdict(self, voxel: Voxel):
        """
        Get a dictionary of all possible symlists containing the Voxel object
        """
        symdict = {}
        for voxel2 in self.Lattice.VoxelDict.values():
            voxel_pair = frozenset([voxel.index, voxel2.index])
            current_symlist = self.symlist(voxel_pair)
            # Only add symlists for voxel pairs with valid symmetries
            if len(current_symlist) > 0:
                symdict[voxel_pair] = current_symlist
        return symdict

if __name__ == '__main__':
    # Test SymmetryDf class
    SymDf = SymmetryDf()
    double_rotations = SymDf.init_double_rotations()
    for index, rotation in enumerate(double_rotations.keys()):
        print(f'Rotation {index+1}: {rotation}')
    print(f'Number of double rotations: {len(double_rotations)}')