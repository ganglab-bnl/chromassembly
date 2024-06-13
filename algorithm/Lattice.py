import numpy as np


class Lattice:
    def __init__(self, input_lattice):
        """Initialize a matrix of voxels forming the unit cell in 3D space.
        @param:
            - input_lattice:  3D np.array of ints (direct output from LatticeCreator)
        
        Attributes:
            - voxels: List of Voxel objects in the unit cell
            - UnitCell: 3D np.array of ints, has repeated x, y, z layers
            - MinDesign: 3D np.array of ints, minimum copy-pastable design
                -> ints := Voxel.material
        """
        # Was user's design already a unit cell?
        is_unit_cell = self.isUnitCell(input_lattice)

        if is_unit_cell:
            self.UnitCell = input_lattice
            self.MinDesign = input_lattice[:-1, :-1, :-1] # Remove repeated layers
        elif not is_unit_cell:
            self.UnitCell = np.pad(input_lattice, ((0, 1), (0, 1), (0, 1)), 'wrap') # Repeat layers
            self.MinDesign = input_lattice

        self.voxels = self.initVoxelList(self.MinDesign)
    

    def initVoxelList(self, MinDesign):
        """
        Convert a numpy array to a list of voxels.
        @param:
            - MinDesign: 3D numpy array of ints, the minimum copy-pastable design
        @return:
            - voxels: Ordered list of Voxel objects
        """
        from .Voxel import Voxel
        voxels = []
        index = 0
        for coordinate, value in np.ndenumerate(MinDesign):
            # Create and append voxel with value(material) and index(coordinates)
            current_voxel = Voxel(value, coordinate, index)
            voxels.append(current_voxel)
            index += 1
        return voxels


    def isUnitCell(self, lattice):
        """
        Returns whether a given lattice (np.array) is a unit cell.
        @param:
            - lattice: 3D numpy array of ints (direct output from LatticeCreator)
        @return:
            - is_unit_cell: bool
        """
        z_len, x_len, y_len = lattice.shape
        x_repeat, y_repeat, z_repeat = False, False, False
        is_unit_cell = False
        
        # Check if z, x, or y layers are repeated
        if np.array_equal(lattice[0, :, :], lattice[-1, :, :]) and z_len > 2:
            z_repeat = True
        if np.array_equal(lattice[:, 0, :], lattice[:, -1, :]) and x_len > 2:
            x_repeat = True
        if np.array_equal(lattice[:, :, 0], lattice[:, :, -1]) and y_len > 2: 
            y_repeat = True
        
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