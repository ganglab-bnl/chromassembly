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
                        # print(f'Adding voxel {voxel.id} to complementary_voxels\n---')
                        # print(f'Has the following symmetries with voxel {structural_voxel.id}:\n{symlist}\n')
                        # complementary_voxels.append(voxel)
                        has_symmetry_with_structural_voxel = True
                        break

                if has_symmetry_with_structural_voxel:
                    break
            
            if not has_symmetry_with_structural_voxel:
                structural_voxels.append(voxel) # No symmetries w/ current structural_voxels
        
        return structural_voxels, complementary_voxels
    
    def has_voxel(self, voxel) -> str:
        """
        Check if the voxel is in the mesovoxel.
        """
        if isinstance(voxel, int):
            if voxel in [v.id for v in self.structural_voxels]:
                return 'structural'
            elif voxel in [v.id for v in self.complementary_voxels]:
                return 'complementary'
        else:
            if voxel in self.structural_voxels:
                return 'structural'
            elif voxel in self.complementary_voxels:
                return 'complementary'
        return None

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

    def paint_all_self_symmetries(self, mesovoxel: Mesovoxel):
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
                best_map_parent_id = None
                voxel2_symdict = self.symmetry_df.partner_symdict(voxel2.id)
                for partner_id, symlist in voxel2_symdict.items():
                    # We know voxel2 was kicked out by at least some other voxel in the mesovoxel
                    if partner_id == voxel2.id:
                        continue  # Skip self-symmetry

                    partner_voxel_type = mesovoxel.has_voxel(partner_id)
                    if partner_voxel_type is None:
                        continue

                    best_map_parent_id = partner_id
                    print(f"Setting best map parent for voxel {voxel2.id}: {partner_id}")

                    # Prefer complementary voxels
                    if partner_voxel_type == 'complementary':
                        print(f"And it's complementary!")
                        break
                
                if best_map_parent_id is None:
                    print(f"No best map parent found for voxel {voxel2.id}")
                    continue

                best_map_parent = mesovoxel.lattice.get_voxel(best_map_parent_id) 
                print(f"Found voxel {voxel2.id}'s best map parent: {best_map_parent.id}")
                # --- End of finding best map parent --- #

                # --- If best map parent is a complementary voxel, replace all voxel2's 
                #     bonds with best_map_parent's bonds --- #
                if best_map_parent in mesovoxel.complementary_voxels:
                    symlist = self.symmetry_df.symlist(voxel2.id, best_map_parent.id)
                    for sym_label in symlist:
                        self.copy_paint(best_map_parent, voxel2, sym_label)
                else:
                    # Pop voxel2 into list of complementary voxels
                    mesovoxel.complementary_voxels.append(voxel2)
                    # Map paint the best map parent onto the voxel2
                    map_symlist = self.symmetry_df.symlist(voxel2.id, best_map_parent.id)
                    for sym_label in map_symlist:
                        self.map_paint(best_map_parent, voxel2, sym_label)

                # Paint connecting bond between voxel1 and voxel2
                #TODO: Account for if voxel1 and 2 have any bonds together
                if bond2.color is None:
                    print(f"Painting new bond ({self.n_colors}) between voxel {voxel1.id} and voxel {voxel2.id}")
                    self.n_colors += 1
                    self.paint_bond(bond1, self.n_colors, 'structural')
                    self.paint_bond(bond2, -1*self.n_colors, 'structural')
                else:
                    print(f"Voxel {voxel2.id} already has a bond with color ({bond2.color}), paint its complement ({-1*bond2.color}) onto voxel {voxel1.id}")
                    self.paint_bond(bond1, -1*bond2.color, 'mapped')

                # Distribute colors with self-symmetries
                self.paint_self_symmetries(voxel1)
                self.paint_self_symmetries(voxel2)
                self.paint_self_symmetries(best_map_parent)

                # bond_partner = voxel1.has_bond_partner_with(voxel2)
                # if bond_partner is not None and bond_partner.color is not None:
                #     self.paint_bond(bond1, bond_partner.color, 'mapped')
                #     self.paint_bond(bond2, -1*bond_partner.color, 'mapped')

                # elif bond1.color is None and bond2.color is None: 
                #     self.n_colors += 1
                #     self.paint_bond(bond1, self.n_colors, 'structural')
                #     self.paint_bond(bond2, -1*self.n_colors, 'structural')

                # MapPaint the mesovoxel with the new voxel1
                # voxel1_symdict = self.symmetry_df.partner_symdict(voxel1.id)
                # for sym_voxel_id, symlist in voxel1_symdict.items():
                #     sym_voxel = mesovoxel.lattice.get_voxel(sym_voxel_id)
                #     for sym_label in symlist:
                #         self.map_paint(voxel1, sym_voxel, sym_label) 
                
                # # Repeat for the new voxel2
                # for sym_voxel_id, symlist in voxel2_symdict.items():
                #     sym_voxel = mesovoxel.lattice.get_voxel(sym_voxel_id)
                #     for sym_label in symlist:
                #         self.map_paint(voxel2, sym_voxel, sym_label)


    def paint_bond(self, bond: Bond, color: int, type: str=None) -> None:
        """
        Paint the bond on a given vertex with a given color.
        Optionally, denote whether it is a structural or mapped bond.
        """
        bond.set_color(color)
        bond.set_type(type)

    def paint_self_symmetries(self, voxel: Voxel):
        """
        Paint all self-symmetries for a given voxel.
        """
        print(f'\nPainting all self-symmetries for voxel {voxel.id}')
        self_symlist = self.symmetry_df.symlist(voxel.id, voxel.id)
        for sym_label in self_symlist:
            if sym_label == "translation":
                continue
            self.map_paint(voxel, voxel, sym_label)

    def map_paint(self, parent_voxel: Voxel, child_voxel: Voxel, sym_label: str) -> None:
        """
        Maps all bond colors from a parent voxel onto a child voxel as a result of a
        particular symmetry operation.
        
        @param:
            - parent_voxel: Voxel to -> apply symmetry operation -> map onto child
            - child_voxel: Voxel to receive the mapped bond colors
            - sym_label: name of the symmetry operation to apply
        """
        print(f'MapPaint: parent_voxel {parent_voxel.id} --> {child_voxel.id} with symmetry operation {sym_label}')
        rotated_voxel = self.voxel_rotater.rotate_voxel(parent_voxel, sym_label)

        #TODO: should we also skip if the bond is already painted?
        for direction, parent_bond in rotated_voxel.bonds.items():
            if parent_bond.color is not None:
                child_bond = child_voxel.get_bond(direction)
                if child_bond.color is not None:
                    continue

                self.paint_bond(child_bond, parent_bond.color, 'mapped')
                # self.paint_bond(child_bond.bond_partner, -1*parent_bond.color, 'mapped')
                
                pbond_dirlabel = parent_voxel.get_direction_label(parent_bond.direction)
                cbond_dirlabel = child_voxel.get_direction_label(child_bond.direction)
                print(f'    MapBond ({parent_bond.color}) from parent_bond {pbond_dirlabel} --> child_bond {cbond_dirlabel}')


    def copy_paint(self, parent_voxel: Voxel, child_voxel: Voxel, sym_label: str) -> None:
        print(f"CopyPaint: Replacing all bonds of voxel {child_voxel.id} with bonds of complementary voxel {parent_voxel.id}")
        rotated_voxel = self.voxel_rotater.rotate_voxel(parent_voxel, sym_label)

        #TODO: should we also skip if the bond is already painted?
        for direction, parent_bond in rotated_voxel.bonds.items():
            child_bond = child_voxel.get_bond(direction)
            self.paint_bond(child_bond, parent_bond.color, 'mapped')

            pbond_dirlabel = parent_voxel.get_direction_label(parent_bond.direction)
            cbond_dirlabel = child_voxel.get_direction_label(child_bond.direction)
            print(f'    CopyBond (color = {parent_bond.color}) from parent_bond {pbond_dirlabel} --> child_bond {cbond_dirlabel}')