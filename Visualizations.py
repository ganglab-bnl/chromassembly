import sys
import numpy as np
from vispy import app, scene
from vispy.color import Color

class Visualizer:
    """
    Class to help visualize t.
    """
    def __init__(self, lattice):

        self.lattice = lattice
        self.nlay, self.nrow, self.ncol = lattice.shape
        
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

    def run(self):
        """
        Visualize the lattice in 3D space.
        """
        #TODO: implement diff b/w interactive and non-interactive (add when needed)

        for i in range(8, 10):
            color = Color((np.random.rand(), np.random.rand(), np.random.rand()))
            color.alpha = 1.0
            self.colordict[i] = color

        coords = []
        colors = []
        dist = 40

        for i in range(self.nlay):
            for j in range(self.nrow):
                for k in range(self.ncol):
                    x, y, z = i*dist, j*dist, k*dist
                    color = self.colordict[self.lattice[i, j, k]]
                    colors.append(color.rgba)
                    coords.append((x, y, z))
                    # print(f'Voxel at ({x}, {y}, {z}) has color {color.rgba}')

        coords = np.concatenate([coords, [[0, 0, 0]]], axis=0)
        colors = np.concatenate([colors, [[1, 0, 0, 1]]] * (len(coords) - len(colors)), axis=0)

        vis = scene.visuals.Markers(
            pos = coords,
            size = 20,
            antialias=0,
            face_color=colors,
            edge_color='white',
            edge_width=0,
            scaling=True,
            spherical=True
        )

        vis.parent = self.view.scene
        app.run()