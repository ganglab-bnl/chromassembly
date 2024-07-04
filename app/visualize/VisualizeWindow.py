import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from PyQt6.QtGui import QColor
import numpy as np
import math

from .Voxel import Voxel
from .Bond import Bond

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

        # Add axes
        self.add_axes()

        
    def add_axes(self):
        """Adds 3 arrows indicating x, y, z axes to the view at position -1, -1, -1"""
        axes_directions = [
            np.array([1, 0, 0]), # x
            np.array([0, 1, 0]), # y
            np.array([0, 0, 1]) # z
        ]
        for axis in axes_directions:
            shaft, arrow = Bond.create_bond(-3, -3, -3, axis)
            shaft.translate(-1, -1, -1)
            arrow.translate(-1, -1, -1)
            self.view.addItem(shaft)
            self.view.addItem(arrow)


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
                    voxel_shafts, voxel_arrows = Bond.create_voxel_bonds(
                        x*self.voxel_distance, 
                        y*self.voxel_distance, 
                        z*self.voxel_distance
                    )
                    for shaft, arrow in zip(voxel_shafts, voxel_arrows):
                        self.view.addItem(shaft)
                        self.view.addItem(arrow)

                    # Create the voxel object
                    voxel = Voxel.create_voxel(
                        x*self.voxel_distance, 
                        y*self.voxel_distance, 
                        z*self.voxel_distance,
                        self.colordict[0]
                    )
                    self.view.addItem(voxel) # Add it on top of the bonds


   