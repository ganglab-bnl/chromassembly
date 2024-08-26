import itertools
import math
import sys
from .Lattice import Lattice

class ColorTree:
    def __init__(self, lattice: Lattice):
        """
        Initializes the optimizer with the lattice and all possible color configurations.
        """
        self.lattice = lattice
        self.colordict = lattice.init_colordict()
        self.all_color_configs = self.lattice.init_all_color_configs()
        self.optimal_path = {}

    def optimize(self):
        """
        Finds the optimal path of color configurations that minimizes the unique origami count.
        """
        self.optimal_path = self._find_minimal_path(self.all_color_configs)
        return self.optimal_path
        
    def _find_minimal_path(self, all_color_configs):
        """
        Finds the path with the minimal unique_origami count by testing all possible
        combinations of one color_config from each color.
        """
        colors = all_color_configs.keys()
        color_config_combinations = itertools.product(
            *[[(color, config) for config in configs] for color, configs in all_color_configs.items()]
        )

        num_combinations = math.prod(len(configs) for configs in all_color_configs.values())
        print(f"Searching for minimum origami across {num_combinations} possibilities...")

        min_unique_count = float('inf')
        optimal_path = None

        # Iterate through each combination
        for i, combination in enumerate(color_config_combinations, 1):
            current_path = {color: config for color, config in combination}
            self.lattice.apply_color_configs(current_path)
            unique_count = len(self.lattice.unique_origami())

            # Update the loading message in place
            print(f"Evaluating {i}/{num_combinations}...", end='\r', flush=True)

            if unique_count < min_unique_count:
                min_unique_count = unique_count
                optimal_path = current_path

        # Final message after the loop completes
        print(f"Done! {min_unique_count} minimum unique origami found.")

        return optimal_path

    def print_optimal_path(optimal_path):
        """
        Prints the optimal path of color configurations.
        """
        for color, config in optimal_path.items():
            print(f'\nColor {color}\n--')
            for voxel, complementarity in config.items():
                print(f'Voxel{voxel}: {complementarity}.')