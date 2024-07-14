import numpy as np
import pandas as pd

from .Voxel import Voxel
from .Lattice import Lattice
from .Surroundings import SurroundingsManager

class SymmetryDf:
    """
    Class which stores all combinations of voxel pairs and their symmetries.

    @attr:
        - Lattice: Lattice object
        - SurroundingsManager: SurroundingsManager object
        - symmetry_operations: Dictionary of all possible symmetry operations
        - symmetry_df: Pandas DataFrame object containing all voxel pairs and their symmetries
    
    @methods:
    (internal)
        - init_symmetry_df: Initialize an empty symmetry_df with all possible voxel pairs and symmetry operations
        - compute_all_symmetries: Compute all possible symmetries between all 2-combinations of voxels
        - make_voxel_pair_label: Convert frozenset to string for use in representing voxel pairs in Symmetry
    (external)
        - symlist: Get the list of symmetries for a specific voxel pair
        - symdict: Get a dictionary of all possible symlists containing the Voxel object
    """
    def __init__(self, lattice: Lattice, SurroundingsManager: SurroundingsManager):
        """
        Initialize the SymmetryDf object.
        """
        # Store references to lattice and SurroundingsManager objects for use in symmetry comparisons
        self.Lattice = lattice
        self.SurroundingsManager = SurroundingsManager

        # Create dictionary of all possible symmetry operations
        self.symmetry_operations = RotationManager.init_all_rotations()
        
        # Initialize symmetry_df
        self.symmetry_df = self.init_symmetry_df()

        # Compute all symmetries, filling symmetry_df in place
        self.compute_all_symmetries()


    def init_symmetry_df(self) -> pd.DataFrame:
        """
        Initialize an empty symmetry_df with all possible voxel pairs and symmetry operations
        to be filled later.
        @return:
            - symmetry_df: Pandas DataFrame object
        """
        # Create a list of all possible voxel pairs
        voxel_pairs_set = set()
        for voxel1 in self.Lattice.voxel_list:
            for voxel2 in self.Lattice.voxel_list:
                voxel_pairs_set.add(frozenset([voxel1.index, voxel2.index]))
        
        # Convert the set of frozensets to a list of formatted strings
        # E.g., "frozenset({0, 1})" -> "(0, 1)"
        sorted_voxel_pairs_set = sorted(voxel_pairs_set) # Sort lexicographically
        voxel_pairs = [self.make_voxel_pair_label(pair) for pair in sorted_voxel_pairs_set]

        # Create a dataframe containing True or False for each symmetry operation as the column names
        symmetry_df = pd.DataFrame(index=voxel_pairs, columns=self.symmetry_operations.keys())
        # symmetry_df = symmetry_df.fillna(None) # Fill NaN values with None

        return symmetry_df
    
    
    def compute_all_symmetries(self):
        """
        Compute all possible symmetries between all 2-combinations of voxels
        in the Lattice.MinDesign. Fills self.symmetry_df in place with the results.
        """
        for sym_label, sym_function in self.symmetry_operations.items():

            # Loop through all possible voxel pairs
            for voxel1 in self.Lattice.voxel_list:

                # Transform surroundings of voxel1 once per symmetry
                voxel1_surroundings = self.SurroundingsManager.getVoxelSurroundings(voxel1)
                transformed_voxel1_surroundings = sym_function(voxel1_surroundings)

                for voxel2 in self.Lattice.voxel_list:
                    # Make voxel pair to index into SymmetryDict
                    voxel_pair = frozenset([voxel1.index, voxel2.index])
                    voxel_pair_label = self.make_voxel_pair_label(voxel_pair) # index with str

                    # print(f'Checking symmetry for {voxel_pair_label} with {sym_label}...') # debug
    
                    symmetry_already_computed = not pd.isna(self.symmetry_df.loc[voxel_pair_label, sym_label])

                    if symmetry_already_computed:
                        continue # Symmetry already exists in symmetry_df

                    # Check symmetry:
                    # Two voxels are symmetric if their surroundings are the same after one is transformed
                    voxel2_surroundings = self.SurroundingsManager.getVoxelSurroundings(voxel2)
                    has_symmetry = np.array_equal(transformed_voxel1_surroundings, voxel2_surroundings) 

                    self.symmetry_df.loc[voxel_pair_label, sym_label] = has_symmetry # Store the result in symmetry_df


    def symlist(self, voxel1: int, voxel2: int) -> list[str]:
        """
        Get the list of symmetries for a specific voxel pair
        @param:
            - voxel1: Voxel.index for the first voxel
            - voxel2: Voxel.index for the second voxel (can be the same as voxel1)
        @return:
            - symlist: List of symmetry labels that are valid for the voxel pair
                -> ex: ['90° X-axis', '180° Y-axis']
        """
        voxel_pair = frozenset([voxel1, voxel2])
        voxel_pair_label = self.make_voxel_pair_label(voxel_pair)
        all_symmetries = self.symmetry_df.loc[voxel_pair_label]
        valid_symmetries = all_symmetries[all_symmetries == True].index
        symlist = list(valid_symmetries)
        return symlist
    
    def symdict(self, voxel: int) -> dict[str, list]:
        """
        Get a dictionary of all possible symlists containing the Voxel object

        @param:
            - voxel: Voxel.index (int) to find all possible symlists for
        @return:
            - symdict: Dictionary of all voxel pairs with the given voxel 
                       which have symlists of non-zero length
                -> ex: symdict(voxel1)
                    {"(0, 1)": ['90° X-axis', '180° Y-axis'],
                     "(1, 4)": ['90° Z-axis', '270° X-axis']}
        """
        symdict = {}
        for voxel2 in self.Lattice.voxel_list:
            current_symlist = self.symlist(voxel, voxel2.index)
            # Only add symlists for voxel pairs with valid symmetries
            if len(current_symlist) > 0:
                voxel_pair = frozenset([voxel, voxel2.index])
                voxel_pair_label = self.make_voxel_pair_label(voxel_pair)
                symdict[voxel_pair_label] = current_symlist
        return symdict
    

    @staticmethod
    def make_voxel_pair_label(voxel_pair: frozenset) -> str:
        """
        Convert frozenset to string for use in representing voxel pairs in SymmetryDf
        E.g., "frozenset({0, 1})" -> "(0, 1)"

        @param:
            - voxel_pair: a frozenset of two voxel.indices
        @return:
            - string: str, "(voxel1.index, voxel2.index)"
        """
        # Convert to sorted list for consistency
        sorted_vpair_list = sorted(voxel_pair) 
        # Convert each integer in list to str, join with ", ", then wrap in parentheses
        frozen_str = "(" + ", ".join(map(str, sorted_vpair_list)) + ")" 
        return frozen_str
    
    def print_all_symdicts(self) -> None:
        """
        Print all possible symdicts for all voxels in the Lattice.MinDesign.
        """
        for voxel in self.Lattice.voxel_list:
            print(f'Voxel {voxel.index}\n---\nCoordinates: {voxel.coordinates} Material: {voxel.material}')
            print('Symmetries:')
            for voxel_pair, symlist in self.symdict(voxel.index).items():
                print(f'{voxel_pair}: {symlist}')
            print('\n')
    

class RotationManager:
    """Class to initialize and manage all rotation transformations"""

    # Initialize dictionaries for transformation functions
    translation = {
        'translation': lambda x: x # Identity function
    }
    single_rotations = {
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
    double_rotations = {}

    @classmethod
    def init_double_rotations(cls):
        """
        Initialize double_rotations to contain all possible combinations of single_rotations,
        but excluding double rotations on the same axis.
        @return:
            - double_rotations: Dictionary of lambda functions for double rotations
                                {"label1 + label2": lambda x: rotation2(rotation1(x))}
        """
        frozen_double_rotations = [] # List to store frozensets of double rotations (avoids duplicates)

        for label1 in cls.single_rotations.keys():
            for label2 in cls.single_rotations.keys():
                # Create a frozen set of the pair of rotation labels
                rotation_pair = frozenset([label1, label2])

                # Get the last word in string (the axis) from each rotation label
                rotation1_axis = label1.split(' ')[-1] 
                rotation2_axis = label2.split(' ')[-1]

                # Only consider double rotation if they are on different axes and not already considered
                if rotation1_axis != rotation2_axis and rotation_pair not in frozen_double_rotations:
                    frozen_double_rotations.append(rotation_pair)
        
        # Iterate through list of non-repeating double rotations and create a dictionary of lambda functions
        double_rotations = {}
        for rotation_pair in frozen_double_rotations:
            label1, label2 = rotation_pair
            rotation1, rotation2 = cls.single_rotations[label1], cls.single_rotations[label2]

            double_rotations[f'{label1} + {label2}'] = \
                        lambda x, rotation1=rotation1, rotation2=rotation2: rotation2(rotation1(x))
            
        # Sort the dictionary by key
        sorted_double_rotations = {key: double_rotations[key] for key in sorted(double_rotations)}

        cls.double_rotations = sorted_double_rotations
    
    @staticmethod
    def init_all_rotations() -> dict[str, callable]:
        """
        Initialize all possible rotations for symmetry operations
        @return:
            - all_rotations: Dictionary of all possible rotations
        
        @example:
            {'translation': lambda x: x, 
            '90° X-axis': lambda x: np.rot90(x, 1, (0, 1)), 
            ...}
        """
        RotationManager.init_double_rotations()
        all_rotations = {**RotationManager.translation, 
                         **RotationManager.single_rotations, 
                         **RotationManager.double_rotations}
        return all_rotations
    
