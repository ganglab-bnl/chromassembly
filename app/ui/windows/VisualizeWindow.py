import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from PyQt6.QtGui import QColor
import numpy as np

class VisualizeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Set up the 3D view widget
        self.view = gl.GLViewWidget()
        self.view.setCameraPosition(distance=30)
        self.layout.addWidget(self.view)

        # Ball / arrow parameters
        self.voxel_radius = 0.5
        self.bond_length = 1.0
        self.voxel_distance = 4.0
        self.directions = [(1, 0, 0), (-1, 0, 0),  # +/- x
                           (0, 1, 0), (0, -1, 0),  # +/- y
                           (0, 0, 1), (0, 0, -1)]  # +/- z
        
        # Create the lattice
        self.create_lattice(6, 6, 6)  


    def create_lattice(self, x_dim, y_dim, z_dim):

        for x in range(x_dim):
            for y in range(y_dim):
                for z in range(z_dim):
                    # Create all bonds for the voxel
                    voxel_bonds = self.create_voxel_bonds(
                        x*self.voxel_distance, 
                        y*self.voxel_distance, 
                        z*self.voxel_distance
                    )
                    for bond in voxel_bonds:
                        self.view.addItem(bond)

                    # Create the voxel object
                    voxel = self.create_voxel(
                        x*self.voxel_distance, 
                        y*self.voxel_distance, 
                        z*self.voxel_distance
                    )
                    self.view.addItem(voxel) # Add it on top of the bonds


    def create_voxel(self, x, y, z):
        """Creates a 3d voxel object (a sphere) at the given coordinates."""
        sphere = gl.MeshData.sphere(rows=10, cols=20, radius=self.voxel_radius)
        voxel = gl.GLMeshItem(
            meshdata=sphere,
            smooth=True, 
            color=QColor(200, 200, 200),
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
        voxel_bonds = []
        for dx, dy, dz in self.directions:
            bond = self.create_bond(x, y, z, dx, dy, dz)
            voxel_bonds.append(bond)
        return voxel_bonds

    def create_bond(self, x, y, z, dx, dy, dz):
        """
        Creates a single bond (an arrow) starting from (x,y,z) and pointing toward (dx,dy,dz).
        @param:
            - x, y, z: The starting coordinates of the bond (voxel center)
            - dx, dy, dz: The direction of the bond
        """
        bond_data = np.array([
            [0, 0, 0], 
            [dx*self.bond_length, dy*self.bond_length, dz*self.bond_length]
        ])
        bond_color = QColor(80, 80, 80)
        bond = gl.GLLinePlotItem(pos=bond_data, color=bond_color, width=10, antialias=True)
        bond.translate(x, y, z) # Move the starting position of the arrow 
                                      # to the provided voxel coordinates (sphere center)
        return bond

# Example usage
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = VisualizeWindow()
    window.show()
    sys.exit(app.exec())
