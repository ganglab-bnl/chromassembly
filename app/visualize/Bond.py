import pyqtgraph.opengl as gl
from algorithm.Voxel import Voxel
import numpy as np
from ..config import AppConfig

class Bond:
    # Parameters for drawing bonds as arrows
    bond_length = 1.0

    # Shaft parameters
    shaft_length = bond_length * 0.8
    shaft_radius = 0.05

    # Arrowhead parameters
    arrowhead_length = bond_length * 0.2
    arrowhead_radius = 0.15

    # Directions for each bond using numpy arrays converted to bytes as keys
    directions = [
        np.array([1, 0, 0]),
        np.array([-1, 0, 0]),
        np.array([0, 1, 0]),
        np.array([0, -1, 0]),
        np.array([0, 0, 1]),
        np.array([0, 0, -1])
    ]
    rotate_dict = {
        np.array([1, 0, 0]).tobytes(): (90, 0, 1, 0),   # +x
        np.array([-1, 0, 0]).tobytes(): (-90, 0, 1, 0), # -x
        np.array([0, 1, 0]).tobytes(): (-90, 1, 0, 0),  # +y
        np.array([0, -1, 0]).tobytes(): (90, 1, 0, 0),  # -y
        np.array([0, 0, 1]).tobytes(): (0, 0, 0, 1),    # +z
        np.array([0, 0, -1]).tobytes(): (180, 0, 1, 0)  # -z
    }

    @classmethod
    def create_bond(cls, x, y, z, direction, color=(0.5, 0.5, 0.5, 1)):
        """
        Creates a single arrow starting from (x, y, z) and pointing in [direction]
        @param:
            - x, y, z: The starting coordinates of the arrow (voxel center)
            - direction: The (3d) direction of the arrow as a np.array (i,j,k=1)
                         ex: [1, 0, 0] is the +x direction
        """
        dx, dy, dz = direction
        shaft_mesh = gl.MeshData.cylinder(
            rows=1, cols=3, # How many rows/cols to divide the cylinder into (lower=better performance)
            radius=[cls.shaft_radius, cls.shaft_radius], 
            length=cls.shaft_length
        )

        # Draw with/without shader depending on environment
        if AppConfig.RUNNING_IN_JUPYTER:
            shaft = gl.GLMeshItem(
                meshdata=shaft_mesh, 
                smooth=True, 
                color=color
            )
        else:
            shaft = gl.GLMeshItem(
                meshdata=shaft_mesh, 
                smooth=True, 
                shader='shaded',
                color=color
            )

        # Rotate the shaft to face the correct direction
        shaft_rotation = cls.rotate_dict[direction.tobytes()]
        shaft.rotate(*shaft_rotation)
        shaft.translate(x, y, z) # Move the shaft to face out from center of voxel

        # Create the arrowhead
        arrowhead_mesh = gl.MeshData.cylinder(
            rows=2, cols=5, 
            radius=[cls.arrowhead_radius, 0.0], 
            length=cls.arrowhead_length
        )
        
        # Draw with/without shader depending on environment
        if AppConfig.RUNNING_IN_JUPYTER:
            arrowhead = gl.GLMeshItem(
                meshdata=arrowhead_mesh, 
                smooth=True, 
                color=(0.5, 0.5, 0.5, 1)
            )
        else:
            arrowhead = gl.GLMeshItem(
                meshdata=arrowhead_mesh, 
                smooth=True, 
                shader='shaded',
                color=(0.5, 0.5, 0.5, 1)
            )

        # Rotate the arrowhead to face the correct direction
        arrowhead_rotation = cls.rotate_dict[direction.tobytes()]
        arrowhead.rotate(*arrowhead_rotation)
        arrowhead.translate(x + dx*cls.shaft_length, 
                            y + dy*cls.shaft_length, 
                            z + dz*cls.shaft_length) # Move the arrowhead to the end of the shaft

        return shaft, arrowhead

    # @classmethod
    # def create_voxel_bonds(cls, voxel: Voxel):
    #     """
    #     Creates all 6 bonds (arrows) for each direction in directions 
    #     for a given voxel.
    #     @param:
    #         - voxel: Voxel object to create bonds for
    #     """
    #     bond_shafts = []
    #     bond_arrows = []
    #     # for vertex in voxel.vertices:

    #     return bond_shafts, bond_arrows
    
    @classmethod
    def create_voxel_bonds(cls, x, y, z):
        """
        Creates all 6 bonds (arrows) for each direction in directions 
        for a given voxel.
        @param:
            - voxel: Voxel object to create bonds for
        """
        bond_shafts = []
        bond_arrows = []
        for direction in cls.directions:
            shaft, arrow = cls.create_bond(x, y, z, direction, color=(0.5, 0.5, 0.5, 1))
            bond_shafts.append(shaft)
            bond_arrows.append(arrow)
        return bond_shafts, bond_arrows