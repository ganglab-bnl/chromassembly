import pyqtgraph.opengl as gl

class Voxel:
    voxel_radius = 0.5

    @classmethod
    def create_voxel(cls, x, y, z, color):
        """Creates a 3D voxel object (a sphere) at the given coordinates."""
        sphere = gl.MeshData.sphere(rows=5, cols=5, radius=cls.voxel_radius)
        voxel = gl.GLMeshItem(
            meshdata=sphere,
            smooth=True, 
            color=color,
            shader='shaded', 
            drawEdges=True
        )
        voxel.translate(x, y, z)
        return voxel
