import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from PyQt6.QtGui import QColor
import numpy as np
import math

class VisualizeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Set up the 3D view widget
        self.view = gl.GLViewWidget()
        self.view.setCameraPosition(distance=30)
        self.layout.addWidget(self.view)

        # Colors
        self.colordict = {
            0: QColor("#AAAAAA"),
            1: QColor("#3781A9"),
            2: QColor("#57ACC1"),
            3: QColor("#7ECD61"),
            4: QColor("#BBE355"),
            5: QColor("#F9E273"),
            6: QColor("#EAAB83"),
            7: QColor("#DC758F"),
        }

        # Ball / arrow parameters
        self.voxel_radius = 0.5
        self.bond_length = 1.0
        self.voxel_distance = 2.5
        self.directions = [(1, 0, 0), (-1, 0, 0),  # +/- x
                           (0, 1, 0), (0, -1, 0),  # +/- y
                           (0, 0, 1), (0, 0, -1)]  # +/- z
        
        # Create the lattice
        self.create_lattice(3, 3, 3)
        self.view.setBackgroundColor(QColor("#efefef"))


    def adjust_camera_to_fit_lattice(self, x_dim, y_dim, z_dim):
        # Compute total length of the lattice in each dimension
        lattice_xlen = (self.voxel_radius*2 + self.voxel_distance) * x_dim
        lattice_ylen = (self.voxel_radius*2 + self.voxel_distance) * y_dim
        lattice_zlen = (self.voxel_radius*2 + self.voxel_distance) * z_dim

        # Calculate the radius of the sphere that encloses the lattice
        # This is the distance from the center of the lattice to a corner
        half_diagonal = math.sqrt(lattice_xlen**2 + lattice_ylen**2 + lattice_zlen**2) / 2
        
        # Assuming a default FOV of 60 degrees for the camera. Adjust as necessary.
        fov_rad = math.radians(60 / 2)  # Half FOV in radians
        distance = half_diagonal / math.sin(fov_rad)  # Calculate the necessary distance
        
        # Set the camera position to ensure the entire lattice is visible
        self.view.setCameraPosition(distance=distance)


    def create_lattice(self, x_dim, y_dim, z_dim):
        """Creates a default lattice with the specified dimensions"""
        self.adjust_camera_to_fit_lattice(x_dim, y_dim, z_dim)
        for x in range(x_dim):
            for y in range(y_dim):
                for z in range(z_dim):
                    # Create all bonds for the voxel
                    voxel_shafts, voxel_arrows = self.create_voxel_bonds(
                        x*self.voxel_distance, 
                        y*self.voxel_distance, 
                        z*self.voxel_distance
                    )
                    for shaft, arrow in zip(voxel_shafts, voxel_arrows):
                        self.view.addItem(shaft)
                        self.view.addItem(arrow)

                    # Create the voxel object
                    voxel = self.create_voxel(
                        x*self.voxel_distance, 
                        y*self.voxel_distance, 
                        z*self.voxel_distance
                    )
                    self.view.addItem(voxel) # Add it on top of the bonds


    def create_voxel(self, x, y, z):
        """Creates a 3d voxel object (a sphere) at the given coordinates."""
        sphere = gl.MeshData.sphere(rows=5, cols=5, radius=self.voxel_radius)
        voxel = gl.GLMeshItem(
            meshdata=sphere,
            smooth=True, 
            color=self.colordict[0],
            shader='shaded', 
            drawEdges=True
        )
        voxel.translate(x, y, z)
        return voxel

    def create_voxel_bonds(self, x, y, z):
        """
        Creates all 6 bonds (arrows) for each direction in self.directions 
        for a given voxel.
        @param:
            - x, y, z: The coordinates of the voxel
        """
        bond_shafts = []
        bond_arrows = []
        for direction in self.directions:
            shaft, arrow = self.create_bond(x, y, z, direction)
            bond_shafts.append(shaft)
            bond_arrows.append(arrow)
        return bond_shafts, bond_arrows

    def create_bond(self, x, y, z, direction):
        """
        Creates a single arrow starting from (x, y, z) and pointing in [direction]
        @param:
            - x, y, z: The starting coordinates of the arrow (voxel center)
            - [direction]: The (3d) direction of the arrow as a np.array (i,j,k=1)
        """
        dx, dy, dz = direction

        # Create the shaft of the arrow as a cylinder
        self.shaft_length = self.bond_length * 0.8  # Adjust shaft length to leave room for the arrowhead
        shaft_radius = 0.05  # Radius of the shaft
        shaft_mesh = gl.MeshData.cylinder(rows=1, cols=3, radius=[shaft_radius, shaft_radius], length=self.shaft_length)
        shaft = gl.GLMeshItem(meshdata=shaft_mesh, smooth=True, color=(0.5, 0.5, 0.5, 1), shader='shaded')

        # Rotate the shaft to face the correct direction
        if dx == 1:
            shaft.rotate(90, 0, 1, 0)
        elif dx == -1:
            shaft.rotate(-90, 0, 1, 0)
        if dy == 1:
            shaft.rotate(90, 1, 0, 0)
        elif dy == -1:
            shaft.rotate(-90, 1, 0, 0)
        if dz == 1:
            shaft.rotate(0, 0, 0, 1)
        elif dz == -1:
            shaft.rotate(180, 0, 1, 0)

        shaft.translate(x, y, z)

        # Create the arrowhead
        arrowhead_length = self.bond_length * 0.2  # Length of the arrowhead
        arrowhead_radius = self.voxel_radius * 0.3  # Radius of the arrowhead base
        arrowhead_mesh = gl.MeshData.cylinder(rows=2, cols=5, radius=[arrowhead_radius, 0.0], length=arrowhead_length)
        arrowhead = gl.GLMeshItem(meshdata=arrowhead_mesh, smooth=True, color=(0.5, 0.5, 0.5, 1), shader='shaded')

        # Rotate the arrowhead to face the correct direction
        if dx == 1:
            arrowhead.rotate(90, 0, 1, 0)
        elif dx == -1:
            arrowhead.rotate(-90, 0, 1, 0)
        if dy == 1:
            arrowhead.rotate(-90, 1, 0, 0)
        elif dy == -1:
            arrowhead.rotate(90, 1, 0, 0)
        if dz == 1:
            arrowhead.rotate(0, 0, 0, 1)
        elif dz == -1:
            arrowhead.rotate(180, 0, 1, 0)

        arrowhead.translate(x + dx*self.shaft_length, y + dy*self.shaft_length, z + dz*self.shaft_length)

        return shaft, arrowhead

# Example usage
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = VisualizeWindow()
    window.show()
    sys.exit(app.exec())
