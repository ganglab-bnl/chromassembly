import numpy as np
from math import ceil, floor
from .Voxel import Voxel
from .Lattice import Lattice


class SurroundingsManager:
    def __init__(self, lattice: Lattice):
        """
        Manager class for creating, transforming, and comparing VoxelSurroundings
        matrices for a given lattice design.
        """
        self.max_len = max(np.shape(lattice.MinDesign))
        self.lattice = lattice # ref to Lattice object

        self.FullSurroundings = self.initFullSurroundings(lattice)


    def initFullSurroundings(self, lattice: Lattice):
        """
        Initialize a FullSurroundings from all voxels in Lattice.MinDesign,
        which all other SurroundingsMatrices will be subset from.
        @param:
            - lattice: A Lattice object
        @return:
            - full_surroundings: 3D numpy array of ints
        """
        max_len = max(np.shape(lattice.MinDesign))
        final_len = 3 * max_len

        # Get dimensions of MinDesign (we are tiling MinDesign)
        z_len, x_len, y_len = lattice.MinDesign.shape

        # I imagine z=layers, x=rows, y=columns
        z_repeats = ceil(final_len / z_len)
        x_repeats = ceil(final_len / x_len) 
        y_repeats = ceil(final_len / y_len) 

        # If x, y, or z repeats are even, add 1 to make them odd
        # (ensures the original voxel is in the center of FullSurroundings)
        if z_repeats % 2 == 0:
            z_repeats += 1
        if x_repeats % 2 == 0:
            x_repeats += 1
        if y_repeats % 2 == 0:
            y_repeats += 1

        # Tile the surroundings matrix [dim]repeats times in each direction
        self.repeats = [z_repeats, x_repeats, y_repeats]
        full_surroundings = np.tile(lattice.MinDesign, self.repeats)

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
        # if self.md_index == 0:
        #surround_dim = +/- (max_dim/2) in all xyz directions, not including voxel

        # How far down to go in each direction
        og_zlen, og_xlen, og_ylen = np.shape(self.lattice.MinDesign)
        z_repeats, x_repeats, y_repeats = self.repeats

        # Get halfway points for each direction
        # (x_0, y_0, z_0) corresponds to the (0,0,0) position of the middle MinDesign
        z_0 = floor(z_repeats / 2) * og_zlen
        x_0 = floor(x_repeats / 2) * og_xlen
        y_0 = floor(y_repeats / 2) * og_ylen

        # Get voxel's new coordinates within middle MinDesign
        vox_z = z_0 + voxel.coordinates[0]
        vox_x = x_0 + voxel.coordinates[1]
        vox_y = y_0 + voxel.coordinates[2]

        max_og_len = max(og_zlen, og_xlen, og_ylen)
        extend_amt = floor(max_og_len / 2)

        VoxelSurrounding = self.FullSurroundings[(vox_z-extend_amt) : (vox_z+extend_amt+1),
                                                 (vox_x-extend_amt) : (vox_x+extend_amt+1),
                                                 (vox_y-extend_amt) : (vox_y+extend_amt+1)]

        return VoxelSurrounding

