import numpy as np
import pandas as pd
from typing import Set
import copy

from .Voxel import Voxel
from .Bond import Bond
from .Lattice import Lattice
from .Surroundings import Surroundings
from .SymmetryDf import SymmetryDf
from .Rotation import VoxelRotater

class Mesovoxel:
    def __init__(self, lattice: Lattice):
        """
        Mesovoxel data structure, which is comprised a set of structural / complementary 
        voxels. 
            - The structural voxel set is defined clearly by symmetries alone
            - The complementary voxel set starts empty, and we add voxels to it 
              1-by-1 as we paint bonds.
        """
        self.structural_voxels = self.init_structural_voxels(lattice, lattice.SymmetryDf)
        self.complementary_voxels: Set[int] = set()

    def init_structural_voxels(self, lattice: Lattice, symmetry_df: SymmetryDf) -> set[int]:
        """
        Initialize a list of structural voxels.
        """
        structural_voxels = set()
        for voxel in lattice.voxel_list:
            # Initialize set with the first voxel in the lattice.MinDesign
            if structural_voxels == []:
                structural_voxels.add(voxel.id)
                continue

            # Check if voxel has symmetry with any current structural_voxels
            partner_symdict = symmetry_df.partner_symdict(voxel.id)
            if not any(sym_partner in structural_voxels for sym_partner in partner_symdict.keys()):
                # If no symmetries, add voxel to structural_voxels!
                structural_voxels.add(voxel.id) 
        
        return structural_voxels
    
    def has_voxel(self, voxel) -> bool:
        """
        Check if the voxel is in the mesovoxel.

        Args:
            voxel: int or Voxel object corresponding to the desired voxel to 
                   check if it's in the mesovoxel

        Returns: 
            bool: Whether voxel is in either structural or complementary voxel sets
        """
        voxel_id = self._handle_voxel_type(voxel)
        if voxel_id in self.structural_voxels or voxel_id in self.complementary_voxels:
            return True
        return False
    
    def get_voxel_type(self, voxel) -> str:
        """
        Get the type of the given voxel in the mesovoxel.
        If not present in the mesovoxel, returns None.

        Args:
            voxel: int or Voxel object 
        Returns:
            str or None: Either "structural" or "complementary" based on voxel's set membership,
                         or None if not in either.
        """
        voxel_id = self._handle_voxel_type(voxel)

        if voxel_id in self.structural_voxels:
            return 'structural'
        elif voxel_id in self.complementary_voxels:
            return 'complementary'
        return None

    # --- Internal --- #
    def _handle_voxel_type(self, voxel) -> int:
        """
        Internal function to convert either 'Voxel' object / int --> voxel_id (int)
        """
        if isinstance(voxel, int):
            return voxel
        elif isinstance(voxel, Voxel):
            return voxel.id
        else:
            raise TypeError(f"Invalid argument type for voxel. Expected 'int' or 'Voxel', got '{type(voxel).__name__}'.")
        
    

class Painter:

    def __init__(self, lattice: Lattice):
        """
        The idea is to create a coloring scheme for the lattice which minimizes 
        the total number of unique origami and number of colors.
        
        Constraints:
            1. Color complementarity: All colors(+) must be binded to its complement(-)
            2. No palindromes: A color(+) and its complement(-) cannot exist on the same voxel

        Note!
            Following from constraint 1, each painting operation (specifically self_sym_paint)
            also modifies the binding of its partner. Thus we return the painted_voxels after
            each painting so we can exploit each color as much as we can.
        """
        # Data structures (class composition!)
        self.lattice = lattice
        self.symmetry_df = lattice.SymmetryDf
        self.mesovoxel = Mesovoxel(lattice)

        # Painting sets
        self.painted_voxels = set() # (int)
        self.child_voxels = set() # (int)

        # Count of total # colors (not including complementary) 
        # used to paint the MinDesign
        self.n_colors = 0 

    def str_paint_lattice(self):
        """Phase 1: Paint all structural bonds in lattice"""
        raise NotImplementedError()

    def comp_paint_lattice(self):
        """Phase 2: Paint all complementary bonds in lattice"""

        for voxel1 in self.lattice.voxel_list:
            for direction in voxel1.vertex_directions:
                bond1 = voxel1.get_bond(direction)
                voxel2, bond2 = voxel1.get_partner(direction)

                if bond1.color is not None and bond2.color is not None:
                    continue

                # Note: Only manipulate painted_voxels in here (for simplicity)
                self.n_colors += 1
                self.comp_paint(bond1, self.n_colors)
                self.comp_paint(bond2, -self.n_colors)

                # Init painted_voxels with voxel1 and 2
                self.painted_voxels.update(tuple(voxel1.id, voxel2.id)) 
                
                # Iterative self_symmetry painting:
                # ---
                # We keep removing / adding more voxels to painted_voxels as our 
                # painting affects the adjacent voxels, until further self_symmetry painting 
                # has no effect.
                while self.painted_voxels:
                    p_voxel = self.painted_voxels.pop()
                    painted_voxels = self.self_sym_paint(p_voxel)
                    self.painted_voxels.update(painted_voxels)

                    # Also, keep track of all non-paint_pair painted_voxels in 
                    # child_voxels (to find best mesoparent in next step)
                    self.child_voxels.update(painted_voxels)

                # Make sure neither voxel1 nor voxel2 are in child_voxels
                self.child_voxels.discard(voxel1.id)
                self.child_voxels.discard(voxel2.id)

                # Finding best mesoparent and mapping
                best_mesoparent = self.find_best_mesoparent(voxel2)
                if best_mesoparent:
                    # "Map" all bonds of the parent onto the child
                    self.map_paint(child_voxel=voxel2, parent_voxel=best_mesoparent)
                elif best_mesoparent is None:
                    self.mesovoxel.complementary_voxels.add(voxel2.id)

                for child_voxel in self.child_voxels:
                    pass

                
        raise NotImplementedError()

    def find_best_mesoparent(self, voxel):
        for 
        raise NotImplementedError()

    def map_paint(parent_voxel: Voxel, child_voxel: Voxel, sym_label: str, flip_complementarity: bool):
        """
        Map the bonds of a parent voxel onto the child voxel, with some rotation (sym_label)
        and either flipping the complementarity of all bonds (if flipping complementarity of voxel) or not.
        """
    
    def comp_paint(bond: Bond, color: int) -> None:
        """
        Paint a complementary bond of a certain color onto bond.
        
        Args:
            bond (Bond): The bond object to paint
            color (int): What color to paint it
        """
        bond.set_color(color)
        bond.set_type("complementary")