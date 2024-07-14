import numpy as np

class Vertex:
    def __init__(self, voxel, coordinates, bond=None, vertex_partner=None):
        """
        A Vertex object associated with a Voxel parent and connected to a Bond.
        @param:
            - voxel: The parent Voxel object
            - coordinates: tuple(int, int, int), euclidean coords of the vertex wrt. voxel @ (0, 0, 0)
            - bond: Reference to the Bond object attached to this vertex
            - vertex_partner: Reference to the Vertex object that this vertex 
                              connects to within the lattice

        This class is created with the suspicion that future voxels may require more 
        precise coordinate encodings of vertex positions.
        """
        self.voxel = voxel
        self.bond = bond
        # For octahedral voxels, possible coordinates are
        # (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)
        # corresponding to +x, -x, +y, -y, +z, -z
        self.coordinates = coordinates # should i rename to 'direction'? lol
        self.vertex_partner = vertex_partner

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
            - np_index: Voxel's coordinates in the Lattice.MinDesign np.array
            - coordinates: Voxel's coordinates in MinDesign -> Euclidean space 
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
            (1, 0, 0), (-1, 0, 0),   # +-x
            (0, 1, 0), (0, -1, 0),   # +-y
            (0, 0, 1), (0, 0, -1)    # +-z
        ]
        self.vertices = self.init_vertices() # Dict of Vertex objects indexable by coordinates

    def init_vertices(self):
        """Initialize the vertices and bonds of the voxel."""
        vertices = []
        for coords in self.vertex_coordinates:
            # Create a new vertex and attach an empty bond to it
            new_vertex = Vertex(voxel=self, coordinates=coords)
            new_bond = Bond(vertex=new_vertex)
            new_vertex.bond = new_bond
            vertices.append(new_vertex)
        return vertices
    
    
    def get_vertex(self, direction) -> Vertex:
        """
        Get the vertex in a given direction.
        @param:
            - direction: tuple(int, int, int) or np.array, the euclidean direction to find 
                         the vertex in, where direction is wrt. the voxel at (0,0,0)
        @return:
            - vertex: Vertex object
        """

        if isinstance(direction, np.ndarray):
            direction = tuple(direction)
        
        vertex_index = self.vertex_coordinates.index(direction)
        return self.vertices[vertex_index]
    

    def get_partner(self, direction: tuple) -> tuple:
        """
        Get the binding partner voxel for the current instance in a given direction.
        @param:
            - direction: tuple(int, int, int) or np.array, the euclidean direction to find 
                         the bond partner in, where direction is wrt. the voxel at (0,0,0)
        @return:
            - partner_voxel: Voxel object
            - partner_vertex: Vertex object on partner_voxel which connects to the current instance
        """
        vertex = self.get_vertex(direction)
        partner_vertex = vertex.vertex_partner

        if partner_vertex is None:
            raise ValueError("Partner vertex not yet initialized")

        partner_voxel = partner_vertex.voxel
        return partner_voxel, partner_vertex


class Bond:
    def __init__(self, vertex: Vertex, color: int=None, bond_partner=None, bond_type=None):
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
        self.bond_type = bond_type

    def set_bond_partner(self, bond_partner):
        """Set the Bond object which this bond is connected to."""
        self.bond_partner = bond_partner

    def set_bond_type(self, bond_type: str):
        """Set bond type to be either a 'structural' or 'mapped' bond."""
        self.bond_type = bond_type

