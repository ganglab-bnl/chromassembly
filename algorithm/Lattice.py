import numpy as np


class Lattice:
    def __init__(self, input_lattice):
        """
        Initialize a matrix of voxels forming the unit cell in 3D space.
        @param:
            - input_lattice:  3D np.array of ints (direct output from LatticeCreator)
        
        @attributes:
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
    

    def initVoxelDict(self, MinDesign):
        """
        Initialize VoxelDict, computing voxel coordinates and creating Voxel objects.
        @param:
            - MinDesign: 3D numpy array of ints, the minimum copy-pastable design
        @return:
            - VoxelDict: Dictionary of Voxel objects indexable by coordinates
        """
        from .Voxel import Voxel
        VoxelDict = {}
        index = 0
        for np_coordinates, value in np.ndenumerate(MinDesign):
            # Create and append voxel with value(material) and 
            # index(coordinates in the np.array) as hashable bytes
            coordinates = self.transform_indices_to_coordinates(MinDesign.shape, np_coordinates)
            current_voxel = Voxel(value, np_coordinates, coordinates, index)
            print(f'Voxel {index} at np_coords: {np_coordinates}, coords: {coordinates} has material {value}')
            VoxelDict[coordinates.tobytes()] = current_voxel # Turn numpy array into hashable bytes
            index += 1
        return VoxelDict
    

    def transform_indices_to_coordinates(self, array_shape, np_coordinates):
        """
        Transforms np_coordinates to coordinates where the bottom left corner 
        of the bottom-most layer is (0, 0, 0). Note that coordinate dimensions are (x, y, z)
        while numpy array dimensions are (z, y, x).
        @param:
            - array_shape: Tuple of ints
            - index: Tuple of ints
        @return: coordinates: Tuple of ints
        """
        z_max, y_max, x_max = array_shape
        z, y, x = np_coordinates

        # Transform indices: reverse z and y, no change to x
        # (See diagram for more details)
        new_z = z_max - 1 - z
        new_y = y_max - 1 - y
        new_x = x

        coordinates = np.array([new_x, new_y, new_z])
        return coordinates

            
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
        # Get the coordinates of the neighboring voxel
        # x, y, z = voxel.coordinates
        # self.directionDict = {
        #     '+x': (1, 0, 0),
        #     '-x': (-1, 0, 0),
        #     '+y': (0, 1, 0),
        #     '-y': (0, -1, 0),
        #     '+z': (0, 0, 1),
        #     '-z': (0, 0, -1)
        # }

        # direction_tuple = self.directionDict[direction]
        partner_coords = voxel.coordinates + direction

        for index, coord in enumerate(partner_coords):
            # Wrap around to find coordinate if out of bounds
            if coord < 0:
                partner_coords[index] = self.MinDesign.shape[index] + coord
            elif coord >= self.MinDesign.shape[index]:
                partner_coords[index] = coord - self.MinDesign.shape[index]

        partner_voxel = self.VoxelDict[partner_coords.tobytes()]

        partner_direction = -direction # Reverse direction to find partner vertex
        partner_vertex = partner_voxel.vertices[partner_direction.tobytes()]
        
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