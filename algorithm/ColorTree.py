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

    def optimize(self, end_early=False):
        """
        Finds the optimal path of color configurations that minimizes the unique origami count.
        """
        self.reduced_color_configs = self._reduce_color_configs(self.all_color_configs)
        self.optimal_path = self._find_minimal_path(self.reduced_color_configs, end_early=end_early)
        return self.optimal_path
    
    def _reduce_color_configs(self, all_color_configs):
        """
        Find the best color configs for each color in the lattice, THEN find the best path.
        """

        new_all_color_configs = {}
        total_colors = len(all_color_configs)

        print(f"Evaluating color-wise configurations for {total_colors} colors...")

        for color_index, (color, configs) in enumerate(all_color_configs.items(), 1):

            best_configs = []
            min_unique_count = float('inf')
            total_configs = len(configs)
            for config_index, config in enumerate(configs, 1):
                color_config = {color: config}
                self.lattice.apply_color_configs(self.lattice.default_color_config) # Reset
                self.lattice.apply_color_configs(color_config)
                unique_count = len(self.lattice.unique_origami())

                # Add the color config to the best_configs list if it has the lowest unique count
                if unique_count < min_unique_count:
                    min_unique_count = unique_count
                    best_configs = [config]
                elif unique_count == min_unique_count:
                    best_configs.append(config)

                # Update the loading message in place
                print(f"Evaluating color {color_index}/{total_colors}, config {config_index}/{total_configs}...", end='\r', flush=True)

            new_all_color_configs[color] = best_configs

        # Final message after the loop completes
        print("\nDone with color-wise evaluation.")

        return new_all_color_configs
        
    def _recompute_color_config_combinations(self, all_color_configs):
        """
        Recomputes the color config combinations based on the reduced color configs.
        """
        reduced_color_configs = self._reduce_color_configs(all_color_configs)
        # color_config_combinations = itertools.product(
        #     *[[(color, config) for config in configs] for color, configs in reduced_color_configs.items()]
        # )
        num_combinations = math.prod(len(configs) for configs in all_color_configs.values())
        return num_combinations
    
    def _find_minimal_path(self, all_color_configs, end_early=False):
        """
        Finds the path with the minimal unique_origami count by testing all possible
        combinations of one color_config from each color.
        """
        count = 0

        colors = all_color_configs.keys()
        color_config_combinations = itertools.product(
            *[[(color, config) for config in configs] for color, configs in all_color_configs.items()]
        )

        # all_color_configs = lattice.init_all_color_configs()
        for color in all_color_configs:
            print(f'Color {color} has {len(all_color_configs[color])} configurations.')

        num_combinations = math.prod(len(configs) for configs in all_color_configs.values())
        print(f"Searching for minimum origami across {num_combinations} possibilities...")

        min_unique_count = len(self.lattice.unique_origami())
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

                # Recompute the reduced color configs with the new optimal path
                new_all_color_configs = self.lattice.init_all_color_configs()
                self.reduced_color_configs = self._reduce_color_configs(new_all_color_configs)
                new_num_combinations = self._recompute_color_config_combinations(self.reduced_color_configs)

                if new_num_combinations < num_combinations:

                    # Rerun the search with the updated configs
                    print(f"Found {min_unique_count} new minimum unique origami. Reducing search space to {new_num_combinations} possibilities...")
                    return self._find_minimal_path(self.reduced_color_configs, end_early=end_early)

                # count += 1

                # if end_early is True and count == 1:
                #     print(f"Ending early after finding {min_unique_count} minimum unique origami.")
                #     return optimal_path

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
