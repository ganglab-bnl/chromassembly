import numpy as np
import pandas as pd

from .Voxel import Voxel
from .Bond import Bond
from .Lattice import Lattice
from .Surroundings import SurroundingsManager
from .SymmetryDf import SymmetryDf
from .RotationDict import VoxelRotater

class Mesovoxel:
    def __init__(self, lattice: Lattice, symmetry_df: SymmetryDf):
        """
        Mesovoxel to manipulate set of structural / complementary voxels as we paint.
        """
        self.lattice = lattice
        self.symmetry_df = symmetry_df
        self.structural_voxels, self.complementary_voxels = self.init_mesovoxel(lattice)
        

    def init_mesovoxel(self, lattice: Lattice) -> tuple[list[Voxel], list[Voxel]]:
        """
        Initialize a list of structural voxels.
        """
        structural_voxels = []
        complementary_voxels = []

        for voxel in lattice.voxel_list:

            if structural_voxels == []:
                structural_voxels.append(voxel)
                continue

            partner_symdict = self.symmetry_df.partner_symdict(voxel.id)

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
    def __init__(self, lattice: Lattice, 
                 SurroundingsManager: SurroundingsManager, 
                 SymmetryDf: SymmetryDf):
        """
        Manager class for coloring bonds between voxels in a lattice.
        """
        self.lattice = lattice
        self.SM = SurroundingsManager
        self.symmetry_df = SymmetryDf
        self.voxel_rotater = VoxelRotater()
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
                    self.paint_bond(bond, self.n_colors, 'structural')
                    self.paint_bond(partner_bond, -1*self.n_colors, 'structural')
                    print(f'Paint bond with color ({self.n_colors}):\nBetween voxel {structural_voxel.id} ({bond.direction}) and voxel {partner_voxel.id} ({partner_bond.direction})\n')

    def paint_self_symmetries(self, mesovoxel: Mesovoxel):
        """
        Paint all self-symmetries for each structural voxel in the Mesovoxel
        """
        for structural_voxel in mesovoxel.structural_voxels:
            self_symlist = self.symmetry_df.symlist(structural_voxel.id, structural_voxel.id)
            if self_symlist is None:
                continue
            for symmetry_label in self_symlist:
                if symmetry_label == "translation":
                    continue
                print(f'(self)MapPainting voxel {structural_voxel.id} with symmetry operation {symmetry_label}')
                self.map_paint(structural_voxel, structural_voxel, symmetry_label)
        
    def main_loop(self, mesovoxel: Mesovoxel):
        """
        Main loop to paint all bonds in the mesovoxel.
        """
        for voxel1 in mesovoxel.lattice.voxel_list:
            for direction in voxel1.vertex_directions:
                bond1 = voxel1.get_bond(direction)
                voxel2, bond2 = voxel1.get_partner(direction)

                # Skip vertices with already painted bonds
                if bond1.color is not None:
                    continue

                # --- Find the best map parent in the mesovoxel --- #
                voxel2_symdict = self.symmetry_df.partner_symdict(voxel2.id)
                for partner_id, symlist in voxel2_symdict.items():
                    # Skip self-symmetry - we know voxel2 was kicked out by at least some other voxel
                    if partner_id ==voxel2.id:
                        continue 

                    best_map_parent_id = partner_id

                    # Prefer complementary voxels
                    if partner_id in mesovoxel.complementary_voxels: 
                        best_map_parent_id = partner_id 
                        break
                best_map_parent = mesovoxel.lattice.get_voxel(best_map_parent_id) 
                print(f"Found voxel {voxel2.id}'s best map parent: {best_map_parent_id}")
                # --- End of finding best map parent --- #

                # Map paint the best map parent onto the voxel2
                map_symlist = self.symmetry_df.symlist(voxel2.id, best_map_parent_id)
                for sym_label in map_symlist:
                    print(f'MapPainting voxel {best_map_parent_id} onto voxel {voxel2.id} with symmetry operation {sym_label}')
                    self.map_paint(best_map_parent, voxel2, sym_label)

                # Paint connecting bond between voxel1 and voxel2
                #TODO: Account for if voxel1 and 2 have any bonds together
                self.n_colors += 1
                self.paint_bond(bond1, self.n_colors, 'structural')
                self.paint_bond(bond2, -1*self.n_colors, 'structural')

                # MapPaint the mesovoxel with new voxel2
                for sym_voxel_id, symlist in voxel2_symdict.items():
                    for sym_label in symlist:
                        print(f'MapPainting voxel {voxel2.id} onto {sym_voxel_id} with symmetry operation {sym_label}')
                        sym_voxel = mesovoxel.lattice.get_voxel(sym_voxel_id)
                        self.map_paint(voxel2, sym_voxel, sym_label)


    def paint_bond(self, bond: Bond, color: int, type: str=None) -> None:
        """
        Paint the bond on a given vertex with a given color.
        Optionally, denote whether it is a structural or mapped bond.
        """
        bond.set_color(color)
        bond.set_type(type)

    def map_paint(self, parent_voxel: Voxel, child_voxel: Voxel, sym_label: str) -> None:
        """
        Maps all bond colors from a parent voxel onto a child voxel as a result of a
        particular symmetry operation.
        
        @param:
            - parent_voxel: Voxel to -> apply symmetry operation -> map onto child
            - child_voxel: Voxel to receive the mapped bond colors
            - sym_label: name of the symmetry operation to apply
        """
        rotated_voxel = self.voxel_rotater.rotate_voxel(parent_voxel, sym_label)

        #TODO: should we also skip if the bond is already painted?
        for direction, parent_bond in rotated_voxel.bonds.items():
            if parent_bond.color is not None:
                child_bond = child_voxel.get_bond(direction)
                if child_bond.color is not None:
                    continue
                self.paint_bond(child_bond, parent_bond.color, 'mapped')
                print(f'MapBond (color = {parent_bond.color}) from bond {parent_bond.direction} -> bond {child_bond.direction}')