import numpy as np
# from .Voxel import Voxel, Vertex
from .Voxel2 import Voxel
from .Bond import Bond


class Lattice:
    """
    Lattice class to store and manage a 3D lattice of voxels.

    @attr:
        - UnitCell: 3D np.array(ints), has repeated x, y, z layers
        - MinDesign: 3D np.array(ints), minimum copy-pastable design
            -> int := Voxel.material
            -> Coordinate system based on Voxel location in MinDesign
        - voxel_list: List of Voxel objects
        - coord_list: List of each Voxel's coordinates in euclidean space

    @methods:
        - get_voxel: Get a Voxel object by its index or coordinates
        - get_partner: Get the bond partner of a voxel in a given direction

    @private:
        - _init_voxels: Initializes all Voxel + blank Bond objects and their coordinates
                        in the Lattice.MinDesign
        - _fill_partners: Fills all bond partners on all voxels in voxel_list in place
        - _get_partner: Internal method to get the bond partner of a voxel 
        - _is_unit_cell: Returns whether a given lattice is a unit cell
    """
    
    def __init__(self, input_lattice: np.array):
        """
        Initialize a matrix of voxels forming the unit cell in 3D space.
        @param:
            - input_lattice:  3D np.array of ints (direct output from LatticeCreator)
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

    # Public methods
    def get_voxel(self, voxel_id) -> Voxel:
        """
        Get a Voxel object by its index or coordinates depending on the supplied parameter.
        @param:
            - voxel_id: int (Voxel.index) or tuple/np.ndarray (Voxel.coordinates)
        @return:
            - voxel: The desired Voxel object
        """
        if isinstance(voxel_id, int):
            # Case 1: voxel_id is an index (int)
            voxel_index = voxel_id
        elif isinstance(voxel_id, tuple):
            # Case 2: voxel_id is euclidean coordinates (tuple)
            voxel_index = self.coord_list.index(voxel_id)
        elif isinstance(voxel_id, np.ndarray):
            # Case 3: voxel_id is np.ndarray coordinates
            voxel_index = self.coord_list.index(tuple(voxel_id))
        else:
            # Case 4: Invalid type
            raise ValueError(f"Invalid voxel_id type: {type(voxel_id)}")

        voxel = self.voxel_list[voxel_index] # Omiting error handling because it's self explanatory
        return voxel

    # Internal methods
    def _is_unit_cell(lattice: np.array) -> bool:
        """
        Returns whether a given lattice (np.array) is a unit cell.
        @param:
            - lattice: 3D numpy array of ints (direct output from LatticeCreator)
        @return:
            - is_unit_cell: bool
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

        voxel_id = 0
        # 1. Initialize all voxels with empty vertices
        for np_index, material in np.ndenumerate(MinDesign):
            # Map voxel's numpy index into euclidean space
            coordinates = CoordinateManager.npindex_to_euclidean(np_index, MinDesign.shape)
            
            # Create new Voxel object with given info
            current_voxel = Voxel(
                voxel_id=voxel_id, 
                material=material, 
                coordinates=coordinates, 
                np_index=np_index
            )
            
            # Append current voxel and its coordinates to the lists
            voxel_list.append(current_voxel)
            coord_list.append(coordinates)
            voxel_id += 1

        # Print all voxel indices and coordinates
        voxel_ids = ', '.join(str(voxel.voxel_id) for voxel in voxel_list)
        print(f'Initialized Voxels: {voxel_ids}')
        coords = ', '.join(str(coord) for coord in coord_list)
        print(f'With coordinates: {coords}')

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

                # print(f"Filled partner: Voxel {voxel.voxel_id} [{voxel.material}] ---{direction}---> Voxel {partner_voxel.voxel_id} [{partner_voxel.material}]")
    
    def _get_partner(self, voxel, direction) -> tuple[Voxel, Bond]:
        """
        Get the bond partner of a voxel in a given direction.
        Note that directions are all stored as tuples but need to be converted
        to numpy arrays for element-wise addition.
        @param:
            - voxel: Voxel object, or the voxel_id / coordinates of the desired Voxel
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

    # def _init_vertices(self):
    #     """
    #     Fill all vertex partners on all voxels in voxel_list in place.
    #     """
    #     for voxel in self.voxel_list:
    #         for coords in voxel.vertex_coordinates:
    #             # Get the partner voxel + vertex the voxel is connected to
    #             partner_voxel, partner_vertex = self.get_partner(voxel, coords)
                
    #             # Set the vertex's partner and bond
    #             vertex = voxel.get_vertex(coords)
    #             vertex.vertex_partner = partner_vertex
    #             vertex.bond.set_bond_partner(partner_vertex.bond)
    

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