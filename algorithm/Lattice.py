"""A Lattice class to store and manage a 3D lattice of voxels.

The central class containing the Voxels + Bonds to be manipulated in 
place by the coloring algorithm. Also contains all necessary components to
color the lattice, including the Surroundings and SymmetryDf objects.

Need to call Lattice.compute_symmetries() to fill the SymmetryDf in place.

Instances of this class are the direct input to the Visualizer GUI.
"""

import numpy as np
import pandas as pd
from collections import defaultdict
import itertools
import copy
from .Voxel import Voxel
from .Bond import Bond
from .Rotation import VoxelRotater

class Lattice:
    """
    Lattice class to store and manage a 3D lattice of voxels.

    Attributes:
        UnitCell: 3D np.array(ints), has repeated x, y, z layers
        MinDesign: 3D np.array(ints), minimum copy-pastable design
            - int := Voxel.material
            - Coordinate system based on Voxel location in MinDesign
        voxel_list: List of Voxel objects
        coord_list: List of each Voxel's coordinates in euclidean space

    Methods:
        get_voxel: Get a Voxel object by its index or coordinates
        get_partner: Get the bond partner of a voxel in a given direction
        _is_unit_cell: Returns whether a given lattice is a unit cell
        _init_voxels: Initializes all Voxel + blank Bond objects and their coordinates
                        in the Lattice.MinDesign
        _fill_partners: Fills all bond partners on all voxels in voxel_list in place
        _get_partner: Internal method to get the bond partner of a voxel (for _fill_partners)
    """
    
    def __init__(self, input_lattice: np.array):
        """
        Initialize the objects and data structures needed for the coloring algorithm.
        Maps the user's lattice design into 3D space, creates Voxel objects,
        the Surroundings, 
        
        Parameters:
            - input_lattice:  3D np.array of ints (direct output from GUI)
        """
        # Was user's design already a unit cell?
        is_unit_cell = Lattice._is_unit_cell(input_lattice)

        if is_unit_cell:
            self.UnitCell = input_lattice
            self.MinDesign = input_lattice[:-1, :-1, :-1] # Remove repeated layers
        elif not is_unit_cell:
            self.UnitCell = np.pad(input_lattice, ((0, 1), (0, 1), (0, 1)), 'wrap') # Repeat layers
            self.MinDesign = input_lattice

        self.voxel_list, self.coord_list = self._init_voxels(self.MinDesign)
        self._fill_partners()

        # Algorithm data structures
        self.VoxelRotater = VoxelRotater()
        self.Surroundings = None
        self.SymmetryDf = None
        self.colordict = None
        self.default_color_config = {}
        self.n_colors = 0

    # --- Public methods ---
    def compute_symmetries(self):
        """
        Compute all symmetries for the Lattice and fill the SymmetryDf.
        Fills in self.Surroundings, which is needed to fill self.SymmetryDf in place.
        """
        from .Surroundings import Surroundings
        from .SymmetryDf import SymmetryDf

        # Initializing Surroundings + SymmetryDf (order matters)
        # computes all symmetries in place and fills a dataframe, 'SymmetryDf'
        # with all possible voxel pairs and their symmetries
        self.Surroundings = Surroundings(self)
        self.SymmetryDf = SymmetryDf(self)

    def get_voxel(self, id) -> Voxel:
        """
        Get a Voxel object by its index or coordinates depending on the supplied parameter.
        @param:
            - id: int (Voxel.index) or tuple/np.ndarray (Voxel.coordinates)
        @return:
            - voxel: The desired Voxel object
        """
        if isinstance(id, int):
            # Case 1: id is an index (int)
            voxel_index = id
        elif isinstance(id, tuple):
            # Case 2: id is euclidean coordinates (tuple)
            voxel_index = self.coord_list.index(id)
        elif isinstance(id, np.ndarray):
            # Case 3: id is np.ndarray coordinates
            voxel_index = self.coord_list.index(tuple(id))
        else:
            # Case 4: Invalid type
            raise ValueError(f"Invalid id type: {type(id)}")

        voxel = self.voxel_list[voxel_index] # Omiting error handling because it's self explanatory
        return voxel

    def final_df(self, show_bond_type=False) -> pd.DataFrame:
        """
        Returns the final dataframe of the lattice.
        """
        # Lists to store combined voxel and bond information
        final_df = []

        # Iterate through the voxels and bonds
        for voxel in self.voxel_list:
            row = {
                ('Voxel', 'ID'): voxel.id,
                ('Voxel', 'Material'): voxel.material,
                ('Voxel', 'Coordinates'): voxel.coordinates
            }
            for direction, bond in voxel.bonds.items():
                bond_label = bond.type if show_bond_type else bond.color
                row[('Bond Colors', bond.get_label())] = bond_label
            final_df.append(row)

        # Create a DataFrame from the combined list
        final_df = pd.DataFrame(final_df)

        # Convert the columns to a MultiIndex
        final_df.columns = pd.MultiIndex.from_tuples(final_df.columns)

        return final_df
    
    def unique_origami(self) -> list[int]:
        """
        Returns a list of unique origami (Voxel+Bonds) in the lattice.
        """
        if self.SymmetryDf is None:
            raise ValueError("SymmetryDf not computed yet. Run Lattice.compute_symmetries() first.")
        
        unique_origami = []
        for voxel1 in self.voxel_list:

            if unique_origami == []:
                unique_origami.append(voxel1.id)
                continue

            is_unique = True
            for voxel2_id in unique_origami:

                voxel2 = self.get_voxel(voxel2_id)
                # Origami can only be non-unique if they share some symmetry
                symlist = self.SymmetryDf.symlist(voxel1.id, voxel2.id)
                if symlist == []:
                    continue

                for sym_label in symlist:
                    rot_voxel_bonds = self.VoxelRotater.rotate_voxel_bonds(voxel1, sym_label)
                    # Check the color of each bond in the rotated voxel
                    if voxel2.is_bond_equal_to(rot_voxel_bonds):
                        is_unique = False
                        break

                if not is_unique:
                    break

            if is_unique:
                unique_origami.append(voxel1.id)

        return unique_origami
    
    
    def init_colordict(self) -> dict[int, list[int]]:
        """
        Get dictionary of all colors in the lattice and a list of their corresponding
        Voxel IDs which contain that color (both color / complement).
        """
        colordict = {}
        for voxel in self.voxel_list:
            for bond in voxel.bonds.values():
                # Don't initialize colordict if not all bonds are colored
                if bond.color is None:
                    raise ValueError(f"Missing colors: Uncolored bond {bond.get_label} on voxel{voxel.id}")
                # Add the bond color to the dictionary
                color = abs(bond.color)
                if color not in colordict:
                    # print(f"Creating new color entry: {color}, voxel{voxel.id}")
                    colordict[color] = [voxel.id]
                elif voxel.id not in colordict[color]:
                    colordict[color].append(voxel.id)
                    # print(f"Adding voxel{voxel.id} to color {color}")

        # Sort the dictionary keys by ascending color
        colordict = {key: colordict[key] for key in sorted(colordict)}
        self.colordict = colordict
                    
        return colordict
    
    def init_all_color_configs(self) -> None:
        """
        Initialize all possible color configurations for all colors in the lattice.
        """
        if self.colordict is None:
            raise ValueError("Color dictionary not initialized yet. Run Lattice.init_colordict() first.")
        
        all_color_configs = {}
        for color in self.colordict.keys():
            all_color_configs[color] = self.color_configs(color)
        
        self.all_color_configs = all_color_configs

        return all_color_configs
    
    def color_configs(self, color: int) -> list[dict[int, int]]:
        """
        Get a list of all complementarity configurations of a given color 
        in the lattice. Each configuration is a dictionary {voxel_id: complementarity}, where
        complementarity is either +1 or -1 and is multiplied to abs(color) to get the bond color
        of those bonds on the voxel.
        """
        if self.colordict is None:
            raise ValueError("Color dictionary not initialized yet. Run Lattice.init_colordict() first.")
        
        color_configs = []
        seen_configs = set()

        # Default configuration
        default_color_config = {}
        for voxel_id in self.colordict[color]:
            voxel = self.get_voxel(voxel_id)
            complementarity = voxel.get_complementarity(color)
            default_color_config[voxel_id] = complementarity

        self.default_color_config[color] = default_color_config

        # Add default configuration to the list and set
        color_configs.append(default_color_config)
        seen_configs.add(tuple(sorted(default_color_config.items())))

        # Get all voxel_ids that contain the color
        voxel_ids = list(self.colordict[color])

        # Iterate over all possible numbers of voxels to flip (1 to len(voxel_ids))
        for r in range(1, len(voxel_ids) + 1):
            # Generate all r-combinations of voxel_ids
            for permutation in itertools.combinations(voxel_ids, r):
                # Create a new color configuration after flipping
                flipped_voxels = {}
                for voxel_id in permutation:
                    voxel = self.get_voxel(voxel_id)
                    flipped_voxels.update(voxel.flip_complementarity(color))

                # Merge flipped configuration with default configuration
                new_color_config = default_color_config.copy()
                new_color_config.update(flipped_voxels)

                # Convert the configuration to a hashable format (tuple of sorted pairs)
                new_config_tuple = tuple(sorted(new_color_config.items()))

                # Check if this configuration is unique
                if new_config_tuple not in seen_configs:
                    color_configs.append(new_color_config)
                    seen_configs.add(new_config_tuple)

        return color_configs

    
    def apply_color_configs(self, color_configs: dict[int, dict[int, int]]) -> None:
        for color, config in color_configs.items():
            for voxel_id, complementarity in config.items():
                voxel = self.get_voxel(voxel_id)
                voxel.repaint_complement(color, complementarity)

    def reset_color_config(self) -> None:
        """
        Reset the color configurations of all voxels to the default configuration.
        """
        self.apply_color_configs(self.default_color_config)

    # --- Internal methods ---
    def _is_unit_cell(lattice: np.ndarray) -> bool:
        """
        Returns whether a given lattice (np.array) is a unit cell.
        
        Args:
            lattice (np.ndarray): 3D numpy array of ints (direct output from LatticeCreator)
        
        Returns:
            is_unit_cell (bool): True if unit_cell, False otherwise
        """
        z_len, y_len, x_len = lattice.shape
        x_repeat, y_repeat, z_repeat = False, False, False
        is_unit_cell = False
        
        # Check if z, y, or x layers are repeated
        if np.array_equal(lattice[0, :, :], lattice[-1, :, :]) and z_len > 2:
            z_repeat = True
        if np.array_equal(lattice[:, 0, :], lattice[:, -1, :]) and x_len > 2:
            y_repeat = True
        if np.array_equal(lattice[:, :, 0], lattice[:, :, -1]) and y_len > 2: 
            x_repeat = True
        
        # If all layers are repeated (and have > 2 dimlength), the lattice is a unit cell
        if x_repeat and y_repeat and z_repeat:
            is_unit_cell = True
        
        return is_unit_cell
    

    def _init_voxels(self, MinDesign: np.array) -> tuple[list[Voxel], list[tuple]]:
        """
        Create Voxel objects for each voxel in MinDesign, filling the following lists:
            - voxel_list: List of Voxel objects
            - coord_list: List of coordinates of each voxel
        where Voxel.index for each voxel can quickly index and retrieve the 
        Voxel object / coordinates from the corresponding list.
        @param:
            - MinDesign: 3D numpy array of ints, the minimum copy-pastable design
        @return:
            - voxel_list: List of Voxel objects
            - coord_list: List of tuples of ints
        """
        voxel_list = []
        coord_list = []

        id = 0
        # 1. Initialize all voxels with empty vertices
        for np_index, material in np.ndenumerate(MinDesign):
            # Map voxel's numpy index into euclidean space
            coordinates = CoordinateManager.npindex_to_euclidean(np_index, MinDesign.shape)
            
            # Create new Voxel object with given info
            current_voxel = Voxel(
                id=id, 
                material=material, 
                coordinates=coordinates, 
                np_index=np_index
            )
            
            # Append current voxel and its coordinates to the lists
            voxel_list.append(current_voxel)
            coord_list.append(coordinates)
            id += 1

        # Print all voxel indices and coordinates
        ids = ', '.join(str(voxel.id) for voxel in voxel_list)
        # print(f'Initialized Voxels: {ids}')
        coords = ', '.join(str(coord) for coord in coord_list)
        # print(f'With coordinates: {coords}')

        return voxel_list, coord_list
    
    def _fill_partners(self):
        """Fill all bond partners on all voxels in voxel_list in place."""
        for voxel in self.voxel_list:
            for direction in voxel.vertex_directions:
                voxel_bond = voxel.get_bond(direction)
                # Skip if bond already has a partner
                if voxel_bond.bond_partner is not None:
                    continue
                # Get the partner bond the voxel is connected to
                partner_voxel, partner_bond = self._get_partner(voxel=voxel, 
                                                                direction=direction)
                # Set the partner_bond attributes on both voxels
                voxel_bond.set_bond_partner(partner_bond)
                partner_bond.set_bond_partner(voxel_bond)

                # print(f"Filled partner: Voxel {voxel.id} [{voxel.material}] ---{direction}---> Voxel {partner_voxel.id} [{partner_voxel.material}]")
    
    def _get_partner(self, voxel, direction) -> tuple[Voxel, Bond]:
        """
        Get the bond partner of a voxel in a given direction.
        Note that directions are all stored as tuples but need to be converted
        to numpy arrays for element-wise addition.
        @param:
            - voxel: Voxel object, or the id / coordinates of the desired Voxel
            - direction: Tuple/np.ndarray of 3 values, the euclidean (x,y,z) direction 
                         to find bond partner in
        @return:
            - partner_voxel: The neighboring voxel object in the supplied direction
            - partner_bond: The bond on partner_voxel which connects to the original voxel
        """
        if isinstance(voxel, int) or isinstance(voxel, tuple):
            voxel = self.get_voxel(voxel)

        if isinstance(direction, np.ndarray):
            direction = tuple(direction)
        
        partner_coords = np.array(voxel.coordinates) + np.array(direction)

        # For each dimension, if out of bounds, wrap around to find MinDesign coord
        for dim_index, coords in enumerate(partner_coords):
            # Define bounds for each dimension
            LOWER_BOUND = 0
            z_max, y_max, x_max = self.MinDesign.shape
            xyz_dimensions = [x_max, y_max, z_max]
            UPPER_BOUND = xyz_dimensions[dim_index]

            # Wrap around to find coordinate if out of bounds
            if coords < LOWER_BOUND:
                partner_coords[dim_index] = UPPER_BOUND + coords
            elif coords >= UPPER_BOUND:
                partner_coords[dim_index] = coords - UPPER_BOUND

        # Get the partner_voxel + vertex the voxel is connected to
        partner_voxel = self.get_voxel(partner_coords)

        partner_vertex_direction = tuple(-np.array(direction)) # Reverse direction to find partner vertex (wrt. partner_voxel)
        partner_bond = partner_voxel.get_bond(partner_vertex_direction)

        # Return the bond partner
        return partner_voxel, partner_bond


class CoordinateManager:
    """
    A utility class to help map a Voxel's numpy array indices to euclidean space.

    Supports the following coordinate types:
        - np_index: tuple(int, int, int) which can be used to index into MinDesign
        - euclidean: tuple(int, int, int) which represents the voxel's coordinates in euclidean space
    """
    def __init__(self):
        pass
    
    @staticmethod
    def npindex_to_euclidean(np_index: tuple, mindesign_shape: tuple) -> tuple:
        """
        Transforms np_index to coordinates where the bottom left corner 
        of the bottom-most layer is (0, 0, 0). Note that coordinate dimensions are (x, y, z)
        while numpy array dimensions are (z, y, x).

        @param:
            - np_index: tuple[int, int, int], the voxel's coordinates within MinDesign
            - mindesign_shape: tuple[int, int, int], shape of the MinDesign np.array
        @return:
            - coordinates: Tuple of ints
        """
        z_max, y_max, x_max = mindesign_shape
        z, y, x = np_index

        # Transform indices: reverse z and y, no change to x
        # (See diagram for more details)
        new_z = z_max - 1 - z
        new_y = y_max - 1 - y
        new_x = x

        euclidean_coords = (new_x, new_y, new_z)
        return euclidean_coords
    
    @staticmethod
    def euclidean_to_npindex(coords, shape):
        raise NotImplementedError("no use yet")