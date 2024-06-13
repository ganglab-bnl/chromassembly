import numpy as np
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



if __name__ == '__main__':
    # Note: To run this file, cd into /algorithm and run 'python3 Voxel.py'
    # (sys.path.append ignores customtkinter otherwise)
    import sys
    sys.path.append('..')
    from visualizations.LatticeCreator import LatticeCreatorGUI
    from visualizations.LatticeVisualizer import LatticeVisualizer
    from .Lattice import Lattice
    from .Surroundings import SurroundingsManager

    # Create a unit cell
    input_lattice, isUnitCell = LatticeCreatorGUI().run()
    lattice = Lattice(input_lattice)
    sm = SurroundingsManager(lattice)

    # Test
    # print(f"Is this a unit cell? {lattice.isUnitCell(input_lattice)}\n")
    # print(f"Unit cell:\n{lattice.UnitCell}\n")

    print(f"Min design:\n{lattice.MinDesign}\n")

    print(f"Full surroundings:\n{sm.FullSurroundings}\n")
    print(f'FullSurroundings shape: {np.shape(sm.FullSurroundings)}')
    print(f'z_repeats: {sm.repeats[0]}, x_repeats: {sm.repeats[1]}, y_repeats: {sm.repeats[2]}')

    # Test getVoxelSurroundings
    voxel = lattice.voxels[0]
    print(f"Voxel 0: {voxel.coordinates}, material: {voxel.material}\n")
    voxel_surroundings = sm.getVoxelSurroundings(voxel)
    print(f"Voxel 0 surroundings:\n{voxel_surroundings}\n")