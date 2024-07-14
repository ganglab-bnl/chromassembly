import sys
import numpy as np
import vispy
vispy.use('PyQt5')
from vispy import app, scene
from vispy.color import Color

class LatticeVisualizer:
    """
    Class to help visualize the input lattice.
    """
    def __init__(self, lattice):

        self.lattice = lattice
        self.n_layers, self.n_rows, self.n_columns = lattice.shape
        
        self.canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)
        self.view = self.canvas.central_widget.add_view()
        self.view.bgcolor = '#efefef'
        self.view.camera = scene.cameras.ArcballCamera(fov=0)
        self.view.camera.scale_factor = 500

        self.colordict = {
            0: Color("#AAAAAA80"),
            1: Color("#3781A9"),
            2: Color("#57ACC1"),
            3: Color("#7ECD61"),
            4: Color("#BBE355"),
            5: Color("#F9E273"),
            6: Color("#EAAB83"),
            7: Color("#DC758F"),
        }

        self.p_dist = 40 # Distance between each visualized particle (ball)

    def create_axes(self):
        axis_end_points = [
            (self.n_layers * self.p_dist, 0, 0),
            (0, self.n_rows * self.p_dist, 0),
            (0, 0, self.n_columns * self.p_dist)
        ]
        labels = ['X', 'Y', 'Z']
        for point, label in zip(axis_end_points, labels):
            text = scene.visuals.Text(label, pos=point, color='black', font_size=20)
            text.parent = self.view.scene


    def run(self):
        """
        Visualize the lattice in 3D space.
        """
        #TODO: implement diff b/w interactive and non-interactive (add when needed)

        # Create a dictionary of random colors for unspecified materials 8-10
        # (can add more or less later)
        for i in range(8, 10):
            color = Color((np.random.rand(), np.random.rand(), np.random.rand()))
            color.alpha = 1.0
            self.colordict[i] = color

        # Determine the coordinates and colors of each voxel (tbe ball / particle) in lattice
        lattice_coords = []
        lattice_colors = []
        for layer in range(self.n_layers):
            for row in range(self.n_rows):
                for column in range(self.n_columns):
                    # Set x, y, z coordinates (to plot) for each voxel
                    x = layer * self.p_dist
                    y = row * self.p_dist
                    z = column * self.p_dist
                    
                    voxel_material = self.lattice[layer, row, column]
                    voxel_color = self.colordict[voxel_material]
                    lattice_colors.append(voxel_color.rgba)
                    lattice_coords.append((x, y, z))
                    # print(f'Voxel at ({x}, {y}, {z}) has color {color.rgba}')

        lattice_coords = np.concatenate([lattice_coords, [[0, 0, 0]]], axis=0)
        lattice_colors = np.concatenate([lattice_colors, [[1, 0, 0, 1]]] * (len(lattice_coords) - len(lattice_colors)), axis=0)

        vispyViewer = scene.visuals.Markers(
            pos = lattice_coords,
            size = 20,
            antialias=0,
            face_color=lattice_colors,
            edge_color='white',
            edge_width=0,
            scaling=True,
            spherical=True
        )
        vispyViewer.parent = self.view.scene
        
        # Create tubes to connect the balls
        for layer in range(self.n_layers):
            for row in range(self.n_rows):
                for column in range(self.n_columns):
                    # Same column and row but different layers
                    if layer < self.n_layers - 1:  
                        start = (layer * self.p_dist, row * self.p_dist, column * self.p_dist)
                        end = ((layer + 1) * self.p_dist, row * self.p_dist, column * self.p_dist)
                        tube = scene.visuals.Tube(np.array([start, end]), color=self.colordict[0].rgba)
                        tube.parent = self.view.scene
                    # Same layer and column but different rows
                    if row < self.n_rows - 1:  
                        start = (layer * self.p_dist, row * self.p_dist, column * self.p_dist)
                        end = (layer * self.p_dist, (row + 1) * self.p_dist, column * self.p_dist)
                        tube = scene.visuals.Tube(np.array([start, end]), color=self.colordict[0].rgba)
                        tube.parent = self.view.scene
                    # Same layer and row but different columns
                    if column < self.n_columns - 1:  
                        start = (layer * self.p_dist, row * self.p_dist, column * self.p_dist)
                        end = (layer * self.p_dist, row * self.p_dist, (column + 1) * self.p_dist)
                        tube = scene.visuals.Tube(np.array([start, end]), color=self.colordict[0].rgba)
                        tube.parent = self.view.scene

        app.run()