import numpy as np
from LatticeCreator import LatticeCreatorGUI

class Voxel:
    def __init__(self, number, material, coordinates, unit_cell):
        """
        Each voxel contains the following information handles:
            - number: Voxel number
            - material: Particle type corresponding to a material
                - 0: empty
                - 1, 2, 3, etc.
            - coordinates: Voxel's coordinates in the user's unit_cell matrix (a x b x c)
            - neighbors: List of direct neighboring voxels in input unit_cell matrix
                +x, -x, +y, -y, +z, -z
            - bind_partners: List of current binding neighbors in each direction; 
                             value is index of neighbor in unit_cell
                +x, -x, +y, -y, +z, -z
            - bind_colors: List of current binding colors in each direction
                +x, -x, +y, -y, +z, -z
            - bparam: List of binding parameters, including binding color and complementarity
            - symmetry: List of all voxels it possesses symmetry with
                - Ordered as [sym_voxel, sym_element(s)]
            
        """
        
        # Fill in material characteristics
        self.number = number
        self.material = material
        self.coordinates = coordinates

        # To be filled in later
        self.neighbors = []
        self.bind_partners = []
        self.bind_colors = []
        self.bparam = []

        # Surrounding matrix
        self.surround_matrix = np.zeros_like(unit_cell)
        
    def set_surround_matrix(self, unit_cell):
        """
        Set the surrounding matrix for the voxel.
        """
        nlay, nrow, ncol = np.shape(unit_cell)
        nrepeat = 3 # Builds surroundings to be +/- 1 unit cell in each direction
        o = int(floor(nrepeat/2)*(nlay-1))
        m = int(floor(nrepeat/2)*(nrow-1))
        p = int(floor(nrepeat/2)*(ncol-1))

        # For each voxel in the unit cell
        for i in range(nlay):
            for j in range(nrow):
                for k in range(ncol):

                    self.surround_matrix[i,j,k] = unit_cell[i,j,k]


class UnitCell:
    def __init__(self, lattice):
        """
        A matrix of voxels forming the unit cell in 3D space.
        @param:
            - lattice: 3D-numpy array of voxels
        Note the right-most column and the bottom-most layer are the repeated boundaries.
        """
        self.lattice = lattice
        self.voxels = self.convert_np_to_voxels(self.lattice)

    # def find_repeat_layers(self, lattice):
    #     """
    #     Find the layers that are repeated in the lattice.
    #     """
    #     repeat_z_layers = []
    #     for i in range(np.shape(lattice)[0]):
    #         if 
    #     return repeat_z_layers
    
    def convert_np_to_voxels(self, lattice):
        """
        Convert a numpy array to a list of voxels.
        """
        voxels = []
        count = 0
        for i in range(np.shape(lattice)[0]):
            for j in range(np.shape(lattice)[1]):
                for k in range(np.shape(lattice)[2]):
                    # Create and append voxel to list
                    vox_coord = (i, j, k)
                    vox = Voxel(count, lattice[i,j,k], vox_coord, lattice)
                    voxels.append(vox)
                    count += 1
        return voxels


if __name__ == '__main__':
    # Create a unit cell
    lattice, isUnitCell = LatticeCreatorGui().run()
    unit_cell = UnitCell(lattice)

    print(f'Original lattice:\n{lattice}\n')
    for voxel in unit_cell.voxels:
        voxel.set_surround_matrix(lattice)
        print(f'\nVoxel {voxel.number} has surrounding matrix:')
        print(voxel.surround_matrix)
        print('\n')
        break # only do once lol
    
    print(f'Lattice shape: {np.shape(lattice)}')
    
