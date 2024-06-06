import numpy as np
from math import ceil

class Voxel:
    def __init__(self, material, coordinates, index):
        """
        A Voxel object containing a particular material 
        and location in the desired Lattice.UnitCell.
        @param:
            - material: int, the material cargo of a voxel
                -> 0: empty
                -> 1=Silver, 2=Gold, 3=(...) etc.
            - coordinates: Voxel's coordinates in the Lattice.MinDesign np.array
            - index: Voxel's index in the Lattice.voxels list
        """
        self.material = material
        self.coordinates = coordinates
        self.index = index

        """
        @old-param (maybe not needed):
            - neighbors: List of direct neighboring voxels in UnitCell
                +x, -x, +y, -y, +z, -z
            - bind_partners: List of current binding neighbors in each direction; 
                             value is index of neighbor in UnitCell
                +x, -x, +y, -y, +z, -z
            - bind_colors: List of current binding colors in each direction
                +x, -x, +y, -y, +z, -z
            - bparam: List of binding parameters, including binding color and complementarity
            - symmetry: List of all voxels it possesses symmetry with
                - Ordered as [sym_voxel, sym_element(s)]
        """
        self.neighbors = []
        self.bind_partners = []
        self.bind_colors = []
        self.bparam = []

        # Surrounding matrix
        # self.surround_matrix = np.zeros_like(unit_cell)
        
    def set_surround_matrix(self, unit_cell):
        """
        Set the surrounding matrix for the voxel.
        """
        n_lay, n_rows, n_col = np.shape(unit_cell)
        


class Bond:
    def __init__(self, voxel1, voxel2, color):
        """
        @param:
            - voxel1:   Voxel object
            - voxel2:   Voxel object
            - color:    Bond color
        """
        self.voxel1 = voxel1
        self.voxel2 = voxel2
        self.color = color

    

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
        x_repeat, y_repeat, z_repeat = False, False, False
        is_unit_cell = False
        
        # Check if z, x, or y layers are repeated
        if np.array_equal(lattice[0, :, :], lattice[-1, :, :]):
            z_repeat = True
        if np.array_equal(lattice[:, 0, :], lattice[:, -1, :]):
            x_repeat = True
        if np.array_equal(lattice[:, :, 0], lattice[:, :, -1]): 
            y_repeat = True
        
        # If all layers are repeated, the lattice is a unit cell
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
    

class SurroundingsManager:
    def __init__(self, lattice: Lattice):
        """
        Manager class for creating, transforming, and comparing VoxelSurroundings
        matrices for a given lattice design."""
        self.FullSurroundings = self.initFullSurroundings(lattice)

    def initFullSurroundings(self, lattice: Lattice):
        """
        Initialize a FullSurroundings for all voxels in Lattice.MinDesign,
        which all other SurroundingsMatrices will be subset from.
        @param:
            - lattice: A Lattice object
        @return:
            - full_surroundings: 3D numpy array of ints
        """
        max_dim = max(np.shape(lattice.MinDesign))
        final_dim = 3 * max_dim

        repeats = [ceil(final_dim / dim) for dim in lattice.MinDesign.shape]
        full_surroundings = np.tile(lattice.MinDesign, repeats)

        return full_surroundings


    def getVoxelSurroundings(self, voxel: Voxel):
        """
        Get the SurroundingsMatrix for a given voxel in the UnitCell, which stores 
        tuples (voxel.material, voxel.index) for each value in the SurroundingsMatrix.
        @param:
            - voxel: The Voxel object to build SurroundingsMatrix around
            - unit_cell: The UnitCell object
        @return:
            - surroundings_matrix: 3D numpy array of tuples (voxel.material, voxel.index) 
        """
        return


if __name__ == '__main__':
    from visualizations.LatticeCreator import LatticeCreatorGUI
    # Create a unit cell
    input_lattice, isUnitCell = LatticeCreatorGUI().run()
    lattice = Lattice(input_lattice)
    SM = SurroundingsManager(lattice)

    # Test
    print(f"Is this a unit cell? {lattice.isUnitCell(input_lattice)}\n")

    print(f"Unit cell:\n{lattice.UnitCell}\n")

    print(f"Min design:\n{lattice.MinDesign}\n")

    print(f"Full surroundings:\n{SM.FullSurroundings}\n")
