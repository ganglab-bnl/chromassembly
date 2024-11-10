import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from PyQt6.QtGui import QColor
import numpy as np
import math
import random

from ..widgets.ToolBar import ToolBar
from .Voxel import Voxel
from .Bond import Bond
from .ColorDict import ColorDict
from algorithm.lattice.Lattice import Lattice

class Visualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Set up the 3D view widget
        self.view = gl.GLViewWidget()
        self.view.setCameraPosition(distance=30)
        self.layout.addWidget(self.view)

        # Colors
        self.colordict = ColorDict(100)

        # Ball / arrow parameters
        self.voxel_radius = 0.5
        self.bond_length = 1.0
        self.voxel_distance = 2.5
        self.directions = [(1, 0, 0), (-1, 0, 0),  # +/- x
                           (0, 1, 0), (0, -1, 0),  # +/- y
                           (0, 0, 1), (0, 0, -1)]  # +/- z
        
        # Create the lattice
        default_lattice = Lattice(np.zeros((3, 3, 3)))
        self.create_lattice(default_lattice)
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
            shaft, arrow = Bond.create_bond_old(-3, -3, -3, axis)
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

    def create_lattice(self, lattice: Lattice):
        """Create lattice from Lattice object"""
        # Delete the current lattice
        self.view.items = []

        # Create the new lattice
        self.add_axes() # Re-add the axes
        n_layers, n_rows, n_columns = lattice.MinDesign.shape
        self.adjust_camera_to_fit_lattice(n_layers, n_rows, n_columns)

        for voxel in lattice.voxels:
            # Create all bonds for the voxel
            # voxel_shafts, voxel_arrows = Bond.create_voxel_bonds(
            #     voxel.coordinates[0]*self.voxel_distance, 
            #     voxel.coordinates[1]*self.voxel_distance, 
            #     voxel.coordinates[2]*self.voxel_distance
            # )
            # for shaft, arrow in zip(voxel_shafts, voxel_arrows):
            #     self.view.addItem(shaft)
            #     self.view.addItem(arrow)

            for _, bond in voxel.bond_dict.dict.items():
                shaft, arrow = Bond.create_bond(bond)
                self.view.addItem(shaft)

                if arrow is not None:
                    self.view.addItem(arrow)

            # Create the voxel object
            new_voxel = Voxel.create_voxel(
                x=voxel.coordinates[0]*self.voxel_distance, 
                y=voxel.coordinates[1]*self.voxel_distance, 
                z=voxel.coordinates[2]*self.voxel_distance,
                color=self.colordict.get_color(voxel.material)
            )
            self.view.addItem(new_voxel)
    

    def cleanup_gl_resources(self):
        """Removes items from view and clears the items list 
           (hopefully preventing jupyter kernel crash on rerun)"""
        for item in self.view.items:
            self.view.removeItem(item)

        self.view.items = []
    
    
class RunVisualizer:
    
    def __init__(self, lattice, app=None):
        """Runs the window for a given lattice design"""
        import sys
        from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar
        from PyQt6.QtCore import Qt
        from ..config import AppConfig

        if app is None:
            self.app = QApplication(sys.argv)
        else:
            self.app = app

        AppConfig.initialize()

        self.mainWindow = QMainWindow()
        self.mainWindow.setWindowTitle("Lattice Visualizer")
        self.mainWindow.setGeometry(100, 100, 800, 600)

        # Create a central widget and set the layout for it
        self.centralWidget = QWidget()
        self.mainLayout = QVBoxLayout(self.centralWidget)
        self.mainWindow.setCentralWidget(self.centralWidget)

        # Initialize VisualizeWindow and add it to the layout
        self.window = Visualizer()
        self.mainLayout.addWidget(self.window)

        # Create and configure the toolbar
        self.toolbar = QToolBar("Main Toolbar", self.mainWindow)
        self.toolbar.setOrientation(Qt.Orientation.Horizontal)
        self.toolbar.addAction("Exit", self.close)
        self.mainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        
        # Draw the lattice structure of voxels + bonds
        self.window.create_lattice(lattice)

        self.mainWindow.show()
        self.app.exec()

    def close(self):
        self.window.cleanup_gl_resources()
        self.app.quit()