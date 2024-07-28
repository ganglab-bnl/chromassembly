import numpy as np
import pandas as pd

from .Voxel2 import Voxel
from .Bond import Bond
from .Lattice import Lattice
from .Surroundings import SurroundingsManager
from .Symmetry import SymmetryDf

class Mesovoxel:
    def __init__(self, Lattice, SymmetryDf):
        """
        Mesovoxel to manipulate set of structural / complementary voxels as we paint.
        """
        self.Lattice = Lattice
        self.SymmetryDf = SymmetryDf
        self.structural_voxels, self.complementary_voxels = self.init_mesovoxel(Lattice)

    def init_mesovoxel(self, Lattice: Lattice):
        """
        Initialize a list of structural voxels.
        """
        structural_voxels = []
        complementary_voxels = []

        for voxel in Lattice.voxel_list:

            if structural_voxels == []:
                structural_voxels.append(voxel)
                continue

            partner_symdict = self.SymmetryDf.partner_symdict(voxel.id)

            for partner_voxel_id, symlist in partner_symdict.items():

                # If voxel has symmetry with a structural voxel already in the list
                # we add it to the list of complementary voxels
                has_symmetry_with_structural_voxel = False
                for structural_voxel in structural_voxels:
                    if partner_voxel_id == structural_voxel.id:
                        print(f'Adding voxel {voxel.id} to complementary_voxels\n---')
                        print(f'Has the following symmetries with voxel {structural_voxel.id}:\n{symlist}\n')
                        complementary_voxels.append(voxel)
                        has_symmetry_with_structural_voxel = True
                        break

                if has_symmetry_with_structural_voxel:
                    break
            
            if not has_symmetry_with_structural_voxel:
                structural_voxels.append(voxel) # No symmetries w/ current structural_voxels
        
        return structural_voxels, complementary_voxels

class BondPainter:
    def __init__(self, Lattice: Lattice, 
                 SurroundingsManager: SurroundingsManager, 
                 SymmetryDf: SymmetryDf):
        """
        Manager class for coloring bonds between voxels in a lattice.
        """
        self.Lattice = Lattice
        self.SM = SurroundingsManager
        self.SymmetryDf = SymmetryDf
        # self.Mesovoxel = Mesovoxel(Lattice, SymmetryDf)

        self.n_colors = 0 # Count of total # colors (not including complementary) used to paint the MinDesign
    
    def paint_mesovoxel(self, Mesovoxel: Mesovoxel):
        """
        Paint all bonds between structural voxels in the Mesovoxel
        """
        for structural_voxel in Mesovoxel.structural_voxels:
            for vertex_direction in structural_voxel.vertex_directions:

                # If vertex already painted, skip
                vertex = structural_voxel.get_vertex(vertex_direction)
                partner_voxel, partner_vertex = structural_voxel.get_partner(vertex_direction)

                if vertex.bond.color is not None or partner_vertex.bond.color is not None:
                    continue

                if partner_voxel in Mesovoxel.structural_voxels:
                    # Always paint complementary bond with opposite (negative) color to the original
                    self.n_colors += 1
                    self.paint_bond(vertex, self.n_colors)
                    self.paint_bond(partner_vertex, -1*self.n_colors)
                    print(f'Paint bond with color ({self.n_colors}):\nBetween voxel {structural_voxel.id} ({vertex.direction}) and voxel {partner_voxel.id} ({partner_vertex.direction})\n')

    
    def paint_bond(self, bond: Bond, color: int, bond_type: str=None):
        """
        Paint the bond on a given vertex with a given color.
        Optionally, denote whether it is a structural or mapped bond.
        """
        vertex.bond.color = color
        vertex.bond.bond_type = bond_type

    def paint_all_bonds(self):
        """
        Paint bonds between voxels in the lattice.
        """
        for voxel1 in self.lattice.VoxelDict.values():
            for vertex_coordinates, vertex1 in voxel1.vertices.items():
                vertex2 = vertex1.vertex_partner
                voxel2 = vertex2.voxel

                # Always paint complementary bond with opposite (negative) color to the original
                self.n_colors += 1
                self.paint_bond(vertex1, self.n_colors)
                self.paint_bond(vertex2, -1*self.n_colors)

                self.RecomputeSymmetries(voxel1)


    def RecomputeSymmetries(self, voxel1):
        """
        Loop to check if painting the new color on the voxel violates any
        previous established symmetries.
        """
        for partner_voxel, symmetry_list in SymmetryDf.symdict(voxel1.id):
            for symmetry_label in symmetry_list:
                #TODO: Change Symmetry obj to store all symmetries in a dict
                pass

    