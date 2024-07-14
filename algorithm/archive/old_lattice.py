import numpy as np


class Lattice:
    def __init__(self, input_lattice):
        """
        Initialize a matrix of voxels forming the unit cell in 3D space.
        @param:
            - input_lattice:  3D np.array of ints (direct output from LatticeCreator)
        
        @attr:
            - VoxelDict: Dictionary of Voxel objects in the unit cell
                -> {coordinates: Voxel object}
            - UnitCell: 3D np.array of ints, has repeated x, y, z layers
            - MinDesign: 3D np.array of ints, minimum copy-pastable design
                -> int := Voxel.material
        """
        # Was user's design already a unit cell?
        is_unit_cell = self.isUnitCell(input_lattice)

        if is_unit_cell:
            self.UnitCell = input_lattice
            self.MinDesign = input_lattice[:-1, :-1, :-1] # Remove repeated layers
        elif not is_unit_cell:
            self.UnitCell = np.pad(input_lattice, ((0, 1), (0, 1), (0, 1)), 'wrap') # Repeat layers
            self.MinDesign = input_lattice

        self.VoxelDict = self.initVoxelDict(self.MinDesign)
        self.voxel_list, self.coord_list = self.init_voxels(self.MinDesign)
    

    def initVoxelDict(self, MinDesign):
        """
        Initialize VoxelDict, computing voxel coordinates and creating Voxel objects.
        @param:
            - MinDesign: 3D numpy array of ints, the minimum copy-pastable design
        @return:
            - VoxelDict: Dictionary of Voxel objects indexable by coordinates
        """
        from ..Voxel import Voxel
        VoxelDict = {}
        index = 0
        for np_index, value in np.ndenumerate(MinDesign):
            # Create and append voxel with value(material) and 
            # index(coordinates in the np.array) as hashable bytes
            coordinates = CoordinateManager.npindex_to_coords(MinDesign.shape, np_index)
            current_voxel = Voxel(index, value, np_index, coordinates)
            print(f'Voxel {index} at np_index: {np_index}, coords: {coordinates} has material {value}')
            
            VoxelDict[tuple(coordinates)] = current_voxel # Turn numpy array into hashable bytes
            index += 1
        return VoxelDict

    def init_voxels(self, MinDesign):
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
        from ..Voxel import Voxel
        voxel_list = []
        coord_list = []

        index = 0
        for np_index, value in np.ndenumerate(MinDesign):
            # Map voxels onto coordinate system
            coordinates = CoordinateManager.npindex_to_coords(MinDesign.shape, np_index)
            current_voxel = Voxel(index, value, np_index, coordinates)

            print(f'Voxel {index} at np_index: {np_index}, coords: {coordinates} has material {value}')
            
            # Append current voxel and its coordinates to the lists
            voxel_list.append(current_voxel)
            coord_list.append(coordinates)
            index += 1

        return voxel_list, coord_list


    # (old method - wrapping logic is sound but updating for np/tuple confusion)
    def getPartner(self, voxel, direction):
        """
        Get the bond partner of a voxel in a given direction.
        @param:
            - voxel: Voxel object
            - direction: np.array of 3 values, the [x,y,z] direction to find bond partner in
        @return:
            - partner_voxel: Voxel object
            - partner_vertex: Vertex on bond_partner which connects to voxel
        """
        partner_coords = voxel.coordinates + direction

        for dim_index, coord in enumerate(partner_coords):
            # Wrap around to find coordinate if out of bounds
            if coord < 0:
                partner_coords[dim_index] = self.MinDesign.shape[dim_index] + coord
            elif coord >= self.MinDesign.shape[dim_index]:
                partner_coords[dim_index] = coord - self.MinDesign.shape[dim_index]

        partner_voxel = self.VoxelDict[tuple(partner_coords)]

        partner_direction = -direction # Reverse direction to find partner vertex
        partner_vertex = partner_voxel.vertices[tuple(partner_direction)]
        
        # Return the bond partner
        return partner_voxel, partner_vertex
    
    def get_partner(self, voxel, direction: tuple):
        """
        Get the bond partner of a voxel in a given direction.
        Note that directions are all stored as tuples but need to be converted
        to numpy arrays for element-wise addition.
        @param:
            - voxel: Voxel object
            - direction: Tuple of 3 values, the (x,y,z) direction to find bond partner in
        @return:
            - partner_voxel: Voxel object
            - partner_vertex: Vertex on bond_partner which connects to voxel
        """
        partner_coords = np.array(voxel.coordinates) + np.array(direction)

        # For each dimension, if out of bounds, wrap around to find MinDesign coord
        for dim_index, coord in enumerate(partner_coords):
            if coord < 0: # Lower bound
                partner_coords[dim_index] = self.MinDesign.shape[dim_index] + coord

            elif coord >= self.MinDesign.shape[dim_index]: # Upper bound
                partner_coords[dim_index] = coord - self.MinDesign.shape[dim_index]

        partner_voxel_index = self.coord_list.index(tuple(partner_coords))
        partner_voxel = self.voxel_list[partner_voxel_index]

        partner_direction = -np.array(direction) # Reverse direction to find partner vertex
        partner_vertex = partner_voxel.vertices[tuple(partner_direction)]

        # Return the bond partner
        return partner_voxel, partner_vertex


    def isUnitCell(self, lattice):
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
        
        # Check if z, x, or y layers are repeated
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
    

    def reduceIfUnitCell(self, lattice, is_unit_cell):
        """
        Remove repeated layers from a lattice if it is a unit cell.
        @param:
            - lattice: 3D numpy array of ints
            - is_unit_cell: bool
        @return:
            - lattice: 3D numpy array of ints, either reduced or the same as input
        """
        if is_unit_cell:
            # Remove repeated layers
            lattice = lattice[:-1, :-1, :-1]
        return lattice
    
    def addRepeatLayers(self, lattice):
        """
        Add repeated layers to a lattice to make it a unit cell.
        @param:
            - lattice: 3D numpy array of ints
        @return:
            - lattice: 3D numpy array of ints, with repeated layers
        """
        lattice = np.pad(lattice, ((0, 1), (0, 1), (0, 1)), 'wrap')
        return lattice
    


class CoordinateManager:
    """
    A utility class to help map a Voxel's numpy array indices to euclidean space.
    """
    def __init__(self):
        pass
    
    @staticmethod
    def npindex_to_coords(np_index, shape):
        """
        Transforms np_index to coordinates where the bottom left corner 
        of the bottom-most layer is (0, 0, 0). Note that coordinate dimensions are (x, y, z)
        while numpy array dimensions are (z, y, x).

        @param:
            - np_index: tuple[int, int, int], the voxel's coordinates within MinDesign
            - shape: tuple[int, int, int], shape of the MinDesign np.array
        @return:
            - coordinates: Tuple of ints
        """
        z_max, y_max, x_max = shape
        z, y, x = np_index

        # Transform indices: reverse z and y, no change to x
        # (See diagram for more details)
        new_z = z_max - 1 - z
        new_y = y_max - 1 - y
        new_x = x

        coordinates = (new_x, new_y, new_z)
        return coordinates
    
    @staticmethod
    def coords_to_npindex(coords, shape):
        raise NotImplementedError("no use yet")