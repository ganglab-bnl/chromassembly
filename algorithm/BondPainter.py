import numpy as np
import pandas as pd

from .Voxel import Voxel
from .Bond import Bond
from .Lattice import Lattice
from .Surroundings import SurroundingsManager
from .SymmetryDf import SymmetryDf

class Mesovoxel:
    def __init__(self, Lattice, SymmetryDf):
        """
        Mesovoxel to manipulate set of structural / complementary voxels as we paint.
        """
        self.Lattice = Lattice
        self.SymmetryDf = SymmetryDf
        self.structural_voxels, self.complementary_voxels = self.init_mesovoxel(Lattice)

    def init_mesovoxel(self, Lattice: Lattice) -> tuple[list[Voxel], list[Voxel]]:
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
        self.lattice = Lattice
        self.SM = SurroundingsManager
        self.symmetry_df = SymmetryDf
        # self.Mesovoxel = Mesovoxel(Lattice, SymmetryDf)

        self.n_colors = 0 # Count of total # colors (not including complementary) used to paint the MinDesign
    
    def paint_mesovoxel(self,mesovoxel: Mesovoxel):
        """
        Paint all bonds between structural voxels in the Mesovoxel
        """
        for structural_voxel in mesovoxel.structural_voxels:
            for direction in structural_voxel.vertex_directions:

                # If vertex already painted, skip
                bond = structural_voxel.get_bond(direction)
                partner_voxel, partner_bond = structural_voxel.get_partner(direction)

                if partner_bond.color is not None or partner_bond.color is not None:
                    continue

                if partner_voxel in mesovoxel.structural_voxels:
                    # Always paint complementary bond with opposite (negative) color to the original
                    self.n_colors += 1
                    self.paint_bond(bond, self.n_colors)
                    self.paint_bond(partner_bond, -1*self.n_colors)
                    print(f'Paint bond with color ({self.n_colors}):\nBetween voxel {structural_voxel.id} ({bond.direction}) and voxel {partner_voxel.id} ({partner_bond.direction})\n')

    def paint_self_symmetries(self, Mesovoxel: Mesovoxel):
        """
        Paint all self-symmetries for each structural voxel in the Mesovoxel
        """
        for structural_voxel in Mesovoxel.structural_voxels:
            self_symlist = self.symmetry_df.symlist(structural_voxel.id, structural_voxel.id)
            if self_symlist is None:
                continue
            for symmetry_label in self_symlist:
                #TODO: vertex rotation
                pass
    
    def paint_bond(self, bond: Bond, color: int, bond_type: str=None):
        """
        Paint the bond on a given vertex with a given color.
        Optionally, denote whether it is a structural or mapped bond.
        """
        bond.set_color(color)
        bond.set_bond_type(bond_type)

    def paint_all_bonds(self):
        """
        Paint bonds between voxels in the lattice.
        """
        for voxel1 in self.lattice.voxel_list:
            for direction in voxel1.vertex_directions():
                bond1 = voxel1.get_bond(direction)
                _, bond2 = voxel1.get_partner(direction)

                # Always paint complementary bond with opposite (negative) color to the original
                self.n_colors += 1
                self.paint_bond(bond1, self.n_colors)
                self.paint_bond(bond2, -1*self.n_colors)

                # self.RecomputeSymmetries(voxel1)


    def RecomputeSymmetries(self, voxel1):
        """
        Loop to check if painting the new color on the voxel violates any
        previous established symmetries.
        """
        for partner_voxel, symmetry_list in SymmetryDf.symdict(voxel1.id):
            for symmetry_label in symmetry_list:
                #TODO: Change Symmetry obj to store all symmetries in a dict
                pass

    