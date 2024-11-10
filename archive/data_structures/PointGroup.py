import numpy as np

from dataclasses import dataclass, field
from typing import Tuple, Dict

@dataclass
class Point:
    """
    The basic Point to manipulate in the PointGroup.
    Contains coordinates and data, where group relations depend on
    the relation of this integer value with another point in a different
    group at the same (or transformed) coordinate.

    Data corresponds to the Voxel material when coords are (0, 0, 0)
    Else, data corresponds to a unique bond 'color' 
    """
    coords: Tuple[float, float, float]
    data: int
    



class PointGroup:
    """
    The PointGroup is a collection of Points corresponding 
    to a unique geometry. Currently, supports octahedra with centered
    material cargo location, but ideally want to extend to custom particle
    orientation within the PointGroup.
    """
    geometry: str # ex: supports "octahedra"
    points: Dict[Tuple[float, float, float], Point] = field(init=False)

    def __post__init__(self):
        """
        Initialize an empty set of points based on user's "geometry" parameter.
        Currently only "octahedron" is supported.

        Very next stage would be to experiment with the coordinates of the "cargo" point.
        """
        if self.geometry == "octahedron":
            self.point_names = [
                # -- Cargo --
                "cargo",
                # -- Vertices --
                "+x", "-x", 
                "+y", "-y", 
                "+z", "-z"
            ]
            # Vector (euclidean) representing direction of each vertex 
            # wrt. the Voxel @ (0,0,0)
            self.point_directions = [
                # -- Cargo --
                (0, 0, 0),
                # -- Vertices --
                (1, 0, 0), (-1, 0, 0),   # +-x
                (0, 1, 0), (0, -1, 0),   # +-y
                (0, 0, 1), (0, 0, -1)    # +-z
            ]

            # Initialize bonds with default values
            self.points = {
                direction: Point(direction=direction, data=None) for direction in self.vertex_directions
            }
        else:
            raise ValueError('Unsupported geometry. Only "octahedron" is supported right now.')
    
    def get_point(self, direction) -> Point:
        """
        Get the Point located in a certain direction.
        
        Args:
            direction: Can be str, np.array, or tuple
        """
        direction = self._handle_direction(direction)
        return self.points.get(direction)
    
    def set_point(self, direction, data: int) -> None:
        """
        Set the data of the point in the given direction.

        Args:
            direction: Can be str, np.array, or tuple
            data (int): Represents either the bond color / cargo material
        """
        point = self.get_point(direction)
        setattr(point, 'data', value=data)


    # -- INTERNAL --
    def _get_direction_label(self, direction) -> str:
        """
        Get the label of the direction (ex: '+x', '-y', etc.)
        """
        direction = self._get_direction_tuple(direction)
        direction_index = self.point_directions.index(direction)
        return self.point_names[direction_index]

    def _handle_direction(self, direction):
        """
        Formats any kind of 'direction' input into a tuple which we can use to
        index into self.bonds

        Handles these kinds of [direction]:
            - str: "+x", "-y", ...
            - np.array: np.array([1, 0, 0]), ...
            - tuple: (1, 0, 0), ...
        """

        try:
            if isinstance(direction, str): 
                # Case 1: direction is a str "+x", "-y", ...
                direction_index = self.vertex_names.index(direction)
                direction = self.vertex_directions[direction_index]

            elif isinstance(direction, np.ndarray): 
                # Case 2: direction is a np.array([1, 0, 0]), ...
                direction = tuple(direction)

        except Exception as ex:
            raise ValueError(f'{ex}: Incorrectly formatted direction.\nDirection should be either str (eg "+x") or np.array or tuple.')
        
        return direction # Now direction is a tuple :-)
    