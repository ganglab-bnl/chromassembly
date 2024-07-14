import numpy as np
class Voxel:
    def __init__(self, index, material, np_index, coordinates):
        """
        A Voxel object containing a particular material and location 
        in the desired Lattice.
        @param:
            - index: Voxel 'number' in the Lattice.VoxelDict
            - material: int, the material cargo of a voxel
                -> 0: empty
                -> 1=silver, 2=gold, 3=(...) etc.
            - np_coordinates: Voxel's coordinates in the Lattice.MinDesign np.array
            - coordinates: Voxel's coordinates in MinDesign -> Cartesian space 
                      (where bottom left corner of bottom layer is 0,0,0)
        """
        self.index = index
        self.material = material
        self.np_index = np_index
        self.coordinates = coordinates

        # Each Voxel contains Vertex and Bond objects in each direction
        # self.vertex_directions = ['+x', '-x', '+y', '-y', '+z', '-z'] # For octahedral voxels
        
        # Coordinates of voxel's vertices with voxel centered at (0, 0, 0)
        self.vertex_coordinates = [
            np.array([1, 0, 0]), np.array([-1, 0, 0]),   # +-x
            np.array([0, 1, 0]), np.array([0, -1, 0]),   # +-y
            np.array([0, 0, 1]), np.array([0, 0, -1])    # +-z
        ]
        self.vertices = self.initVertices() # Dict of Vertex objects indexable by coordinates

    def initVertices(self):
        """Initialize the vertices and bonds of the voxel."""
        vertices = {}
        for coords in self.vertex_coordinates:
            # Create a new vertex and attach an empty bond to it
            new_vertex = Vertex(voxel=self, coordinates=coords)
            new_bond = Bond(vertex=new_vertex)
            new_vertex.bond = new_bond
            # Create dictionary entry for the vertex
            vertices[tuple(coords)] = new_vertex
        return vertices

class Vertex:
    def __init__(self, voxel, coordinates, bond = None, vertex_partner = None):
        """
        A Vertex object associated with a Voxel parent and connected to a Bond.
        @param:
            - voxel: The parent Voxel object
            - coordinates: 3-dimensional tuple, coordinate of the vertex wrt. voxel @ [0, 0, 0]
            - bond: Reference to the Bond object attached to this vertex
            - vertex_partner: Reference to the Vertex object that this vertex 
                              connects to within the lattice

        This class is created with the suspicion that future voxels may require more 
        precise coordinate encodings of vertex positions.
        """
        self.voxel = voxel
        self.bond = bond
        # For octahedral voxels, possible coordinates are
        # [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]
        # corresponding to +x, -x, +y, -y, +z, -z
        self.coordinates = coordinates 
        self.vertex_partner = vertex_partner


class Bond:
    def __init__(self, vertex: Vertex, color: int = None, bond_partner = None, bond_type = None):
        """
        The Bond object which will be colored by the coloring algorithm.
        @param:
            - vertex: Vertex object that the bond is connected to
            - color: int, Bond color
            - bond_partner: Reference to the complementary Bond object that this bond 
                            instance binds with
            - bond_type: str, type of bond (either 'structural' or 'mapped')
        """
        self.vertex = vertex
        self.color = color
        self.bond_partner = bond_partner
        self.bond_type = None

    def setBondPartner(self, bond_partner):
        """Set the Bond object which this bond is connected to."""
        self.bond_partner = bond_partner

    def setBondType(self, bond_type: str):
        """Set bond type to be either a 'structural' or 'mapped' bond."""
        self.bond_type = bond_type



if __name__ == '__main__':
    # Note: To run this file, cd into /algorithm and run 'python3 Voxel.py'
    # (sys.path.append ignores customtkinter otherwise)
    import sys
    sys.path.append('..')
    from visualizations.LatticeCreator import LatticeCreatorGUI
    from visualizations.LatticeVisualizer import LatticeVisualizer
    from .archive.old_lattice import Lattice
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