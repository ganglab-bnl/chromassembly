import pyqtgraph.opengl as gl
from ..config import AppConfig

class Voxel:
    voxel_radius = 0.5

    @classmethod
    def create_voxel(cls, x, y, z, color):
        """Creates a 3D voxel object (a sphere) at the given coordinates."""
        sphere = gl.MeshData.sphere(rows=5, cols=5, radius=cls.voxel_radius)

        # Draw with/without shader depending on environment
        if AppConfig.RUNNING_IN_JUPYTER:
            voxel = gl.GLMeshItem(
            meshdata=sphere,
            smooth=True, 
            color=color,
            drawEdges=True
        )
        else:
            voxel = gl.GLMeshItem(
            meshdata=sphere,
            smooth=True, 
            color=color,
            shader='shaded',
            drawEdges=False
        )

        
        voxel.translate(x, y, z)
        return voxel
