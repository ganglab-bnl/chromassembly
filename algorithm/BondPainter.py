import numpy as np
import pandas as pd

from .Voxel import Voxel, Bond
from .Lattice import Lattice
from .Surroundings import SurroundingsManager
from .Symmetry import SymmetryManager, Symmetry


class BondPainter:
    def __init__(self, lattice: Lattice, SurroundingsManager: SurroundingsManager, SymmetryManager: SymmetryManager):
        """
        Manager class for coloring bonds between voxels in a lattice.
        """
        self.lattice = lattice
        self.sm = SurroundingsManager
        self.symmetry_manager = SymmetryManager

        self.n_colors = 0
    
    
    def paintBond(self, vertex, color: int, bond_type: str=None):
        """
        Paint the bond on a given vertex with a given color.
        Optionally, denote whether it is a structural or mapped bond.
        """
        vertex.bond.color = color
        vertex.bond.bond_type = bond_type

    def paintAllBonds(self):
        """
        Paint bonds between voxels in the lattice.
        """
        for voxel1 in self.lattice.VoxelDict.values():
            for vertex_coordinates, vertex1 in voxel1.vertices.items():
                vertex2 = vertex1.vertex_partner
                voxel2 = vertex2.voxel

                # Always paint complementary bond with opposite (negative) color to the original
                n_colors += 1
                self.paintBond(vertex1, n_colors)
                self.paintBond(vertex2, -1*n_colors)

                self.RecomputeSymmetries(voxel1)


    def RecomputeSymmetries(self, voxel1):
        """
        Loop to check if painting the new color on the voxel violates any
        previous established symmetries.
        """


    def getValidSymmetries(SymmetryDict: dict, voxel: Voxel):
        """
        Create a ValidSymmetries dict where the key is a partner_voxel with some valid 
        symmetry with input voxel. The value is a list of symmetry labels that are valid
        (ex: "90° rotation in X axis")
        contains a specific voxel and the Symmetry.hasAnySymmetry() is True.
        @param:
        - symmetry_dict: dict, where keys are frozensets of integers (voxel.index) 
                         and values are Symmetry objects.
        - voxel: int, index of specific voxel to check for in the keys.

        @return: dict, of {Voxel: [sym1, sym2, ...]} 
        """
        ValidSymmetries = {} # Collect all valid symmetries for voxels containing any sym
        for voxel_set, symmetry_obj in SymmetryDict.items():
            if voxel in voxel_set and symmetry_obj.hasAnySymmetry():
                # Self symmetry
                if len(voxel_set) == 1: 
                    partner_voxel = voxel 
                else: # Get the partner voxel
                    single_voxel_set = (voxel_set - frozenset([voxel]))
                    partner_voxel = single_voxel_set.pop()

                # Get all True symmetries with the partner voxel
                current_symlist = symmetry_obj.getValidSymmetries()
                ValidSymmetries[partner_voxel] = current_symlist

        return ValidSymmetries