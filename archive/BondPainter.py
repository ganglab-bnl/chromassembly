import numpy as np
import pandas as pd
from typing import Set
import copy

from .Voxel import Voxel
from .Bond import Bond
from .Lattice import Lattice
from .Surroundings import Surroundings
from .symmetry_df import SymmetryDf
from .RotationDict import VoxelRotater

class Mesovoxel:
    def __init__(self, lattice: Lattice, symmetry_df: SymmetryDf):
        """
        Mesovoxel to manipulate a set of structural / complementary voxels as we paint.
        """
        self.structural_voxels = self.init_structural_voxels(lattice, symmetry_df)
        self.complementary_voxels: Set[int] = set()

    def init_structural_voxels(self, lattice: Lattice, symmetry_df: SymmetryDf) -> set[int]:
        """
        Initialize a list of structural voxels.
        """
        structural_voxels = set()
        for voxel in lattice.voxels:
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
    
    def has_voxel(self, voxel) -> str:
        """
        Check if the voxel is in the mesovoxel.
        """
        if isinstance(voxel, int):
            if voxel in self.structural_voxels:
                return 'structural'
            elif voxel in self.complementary_voxels:
                return 'complementary'
            
        elif isinstance(voxel, Voxel):
            if voxel.id in self.structural_voxels:
                return 'structural'
            elif voxel.id in self.complementary_voxels:
                return 'complementary'
            
        return None

class BondPainter:
    def __init__(self, lattice: Lattice, symmetry_df: SymmetryDf):
        """
        Manager class for coloring bonds between voxels in a lattice.
        """
        self.lattice = lattice
        self.symmetry_df = symmetry_df
        self.voxel_rotater = VoxelRotater()
        self.mesovoxel = Mesovoxel(lattice, symmetry_df)

        self.n_colors = 0 # Count of total # colors (not including complementary) used to paint the MinDesign
    
    def init_mesopaint(self):
        """
        Paint all bonds between structural voxels in the Mesovoxel
        """
        print("INITIAL MESOVOXEL PAINTING\n---")
        print("Painting all bonds between two structural voxels...")
        for structural_voxel_id in self.mesovoxel.structural_voxels:
            structural_voxel = self.lattice.get_voxel(structural_voxel_id)
            for direction in structural_voxel.vertex_directions:

                # If vertex already painted, skip
                bond = structural_voxel.get_bond(direction)
                partner_voxel, partner_bond = structural_voxel.get_partner(direction)

                if partner_bond.color is not None or partner_bond.color is not None:
                    continue

                if partner_voxel.id in self.mesovoxel.structural_voxels:
                    # Always paint complementary bond with opposite (negative) color to the original
                    self.n_colors += 1
                    self.paint_bond(bond, self.n_colors, 'structural')
                    self.paint_bond(partner_bond, -1*self.n_colors, 'structural')
                    print(f'Paint bond with color ({self.n_colors}):\nBetween voxel {structural_voxel.id} ({bond.direction}) and voxel {partner_voxel.id} ({partner_bond.direction})\n')

                    # Then paint self symmetries for both
                    print("Painting self-symmetries for newly painted structural voxels...")
                    self.paint_self_symmetries(structural_voxel)
                    self.paint_self_symmetries(partner_voxel)

                    # Then map_paint the lattice with both voxels
                    print("Map painting the lattice with newly painted structural voxels...")
                    self.map_paint_lattice(structural_voxel)
                    self.map_paint_lattice(partner_voxel)

    def main_loop3(self):
        """
        My 2nd way of painting the mesovoxel :-)
        """
        print("\nMAIN LOOP 2\n---")
        for voxel1 in self.lattice.voxels:
            # if voxel1.id == 1:
            #     return
            for direction in voxel1.vertex_directions:
                bond1 = voxel1.get_bond(direction)
                voxel2, bond2 = voxel1.get_partner(direction)

                if bond1.color is not None and bond2.color is not None:
                    continue
                    
                # --- Paint connecting bond between voxel1 and voxel2 --- #
                print(f"Paint NEW bond ({self.n_colors})between {voxel1.id} and {voxel2.id}...\n---")
                self.n_colors += 1
                self.paint_bond(bond1, self.n_colors, 'structural')
                self.paint_bond(bond2, -1*self.n_colors, 'structural')

                # Paint self-symmetries for both voxels
                self.paint_self_symmetries(voxel1)
                self.paint_self_symmetries(voxel2)

                # Map paint the lattice with both voxels
                self.map_paint_lattice(voxel1)
                self.map_paint_lattice(voxel2)
                


    def main_loop2(self):
        """
        My way of painting the mesovoxel :-)
        """
        print("\nMAIN LOOP 2\n---")
        for voxel1 in self.lattice.voxels:
            for direction in voxel1.vertex_directions:
                bond1 = voxel1.get_bond(direction)
                voxel2, bond2 = voxel1.get_partner(direction)

                if bond1.color is not None:
                    continue

                # --- Find the best map parent in the mesovoxel --- #
                best_map_parent_id = self.find_best_map_parent(voxel2)
                if best_map_parent_id is None:
                    continue
                best_map_parent = self.lattice.get_voxel(best_map_parent_id)

                # And map best_map_parent's symmetries onto voxel2
                print("\nMap painting all symmetries with best map parent onto voxel2")
                map_symlist = self.symmetry_df.symlist(voxel2.id, best_map_parent.id)
                for sym_label in map_symlist:
                    self.map_paint(best_map_parent, voxel2, sym_label)

                self.mesovoxel.complementary_voxels.add(voxel2.id)

                # --- Distribute bond colors with self-symmetries --- #
                self.paint_self_symmetries(voxel2)

                # --- Paint connecting bond between voxel1 and voxel2 --- #
                print(f"\nPainting bond between {voxel1.id} and {voxel2.id}...\n---")
                if bond1.color is None and bond2.color is None:
                    print(f"Paint NEW bond ({self.n_colors})")
                    self.n_colors += 1
                    self.paint_bond(bond1, self.n_colors, 'structural')
                    self.paint_bond(bond2, -1*self.n_colors, 'structural')

                elif bond1.color is not None and bond2.color is None:
                    print(f"Paint COMPLEMENT bond ({-1*bond1.color}) on voxel {voxel2.id}")
                    self.paint_bond(bond2, -1*bond1.color, bond1.type)

                elif bond1.color is None and bond2.color is not None:
                    print(f"Paint COMPLEMENT bond ({-1*bond2.color}) on voxel {voxel1.id}")
                    self.paint_bond(bond1, -1*bond2.color, bond2.type)

                # --- Distribute bond colors with self-symmetries --- #
                self.paint_self_symmetries(voxel1) 
                self.paint_self_symmetries(voxel2)
                self.paint_self_symmetries(best_map_parent)


    def find_best_map_parent(self, voxel2: Voxel) -> int:
        """Used to find the id of the best parent in the mesovoxel to map onto voxel2"""

        best_map_parent_id = None
        voxel2_symdict = self.symmetry_df.partner_symdict(voxel2.id)

        for partner_id, symlist in voxel2_symdict.items():
            # We know voxel2 was kicked out by at least some other voxel in the mesovoxel
            # Skip self-symmetry
            if partner_id == voxel2.id:
                continue 
            partner_voxel_type = self.mesovoxel.has_voxel(partner_id)
            if partner_voxel_type is None: # Skip voxels not in the mesovoxel
                continue

            best_map_parent_id = partner_id
            print(f"Setting best map parent for voxel {voxel2.id}: {partner_id}")
            # Prefer complementary voxels
            if partner_voxel_type == 'complementary':
                break
        
        if best_map_parent_id is None:
            print(f"No best map parent found for voxel {voxel2.id}")

        print(f"Found voxel {voxel2.id}'s best map parent: {best_map_parent_id}")
        return best_map_parent_id


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
        self_symlist = self.symmetry_df.symlist(voxel.id, voxel.id)
        print(f'\nPAINT SELF SYMMETRIES: Voxel {voxel.id}: {self_symlist}')
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
        print(f'MapPaint: parent_voxel {parent_voxel.id} --> {child_voxel.id} with [{sym_label}] symmetry operation')

        rotated_voxel = self.voxel_rotater.rotate_voxel(parent_voxel, sym_label)
        print(f"---\nRotated Voxel with [{sym_label}]:")
        rotated_voxel.print_bonds()

        print("\nChild Voxel:")
        child_voxel_copy = copy.deepcopy(child_voxel)
        child_voxel_copy.print_bonds()
        print("\n")

        #TODO: Skip the voxel entirely if we reach the bad state
        for direction, parent_bond in rotated_voxel.bond_dict.dict.items():

            if parent_bond.color is None:
                # print(f"    Parent bond {parent_bond.get_label()} is not painted, skipping")
                continue
            
            child_bond_copy = child_voxel_copy.get_bond(direction)
            # Don't MapPaint onto already painted bonds
            if child_bond_copy.color is not None:
                continue
            
            # If child_bond's partner is uncolored, only check palindromic
            map_color = None
            is_palindromic = child_voxel.is_palindromic(parent_bond.color)
            print(f"Palindromic? {is_palindromic}")
            if child_bond_copy.bond_partner.color is None:
                if not is_palindromic:
                    map_color = parent_bond.color
                else:
                    map_color = -1*parent_bond.color
            # If child_bond's partner is colored, check both palindromic and complementarity
            else:
                is_complimentary = child_bond_copy.bond_partner.color == -1*parent_bond.color
                print(f"Complimentary? {is_complimentary}")
                if is_complimentary and not is_palindromic: # Both satisfied
                    map_color = parent_bond.color
                elif not is_complimentary and is_palindromic:
                    map_color = -1*parent_bond.color
                else: # The bad end
                    return
                    # If only one of the conditions is satisfied, don't map paint
                    # the entire voxel
                    #  (avoids infinite loop)

            self.paint_bond(child_bond_copy, map_color, 'mapped')
            # self.paint_bond(child_bond.bond_partner, -1*parent_bond.color, 'mapped')
            # print(f' ---> MapBond ({parent_bond.color}) from parent_bond {parent_bond.get_label()} --> child_bond {child_bond_copy.get_label()}')

        # If we never reached the bad end, set the child_voxel to the mapped copy
        for direction, mapped_bond in child_voxel_copy.bond_dict.dict.items():
            child_voxel.bonds[direction].color = mapped_bond.color
        print("\n")

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

    def map_paint_lattice(self, parent_voxel: Voxel):
        """For each other_voxel in the lattice that is not itself, map_paints 
        its symmetries (those valid symlist items) onto the other_voxel"""
        for child_voxel in self.lattice.voxels:
            if parent_voxel.id == child_voxel.id:
                continue
            symlist = self.symmetry_df.symlist(parent_voxel.id, child_voxel.id)
            for sym_label in symlist:
                self.map_paint(parent_voxel, child_voxel, sym_label)

    # Old method for reference
    def main_loop(self, mesovoxel: Mesovoxel):
        """
        Main loop to paint all bonds in the mesovoxel.
        """
        print("\nMAIN LOOP\n---")
        for voxel1 in mesovoxel.lattice.voxels:

            for direction in voxel1.vertex_directions:
                # Note: Voxel1/bond1 is the outer loop, voxel2/bond2 is the inner loop
                bond1 = voxel1.get_bond(direction)
                voxel2, bond2 = voxel1.get_partner(direction)

                # Skip vertices with already painted bonds
                if bond1.color is not None:
                    # print(f"Voxel {voxel1.id}'s {bond1.get_label()} bond already painted, skipping")
                    continue

                # --- Find the best map parent in the mesovoxel --- #
                best_map_parent_id = self.find_best_map_parent(voxel2, mesovoxel)
                best_map_parent = mesovoxel.lattice.get_voxel(best_map_parent_id)

                # If best map parent is a complementary voxel, replace all voxel2's 
                # bonds with best_map_parent's bonds
                if mesovoxel.has_voxel(best_map_parent) == 'complementary':
                    print(f"Best map parent is a complementary voxel! Copying bonds to voxel {voxel2.id}...")
                    # Replace best_map_parent in mesovoxel.structural_voxels with voxel2
                    mesovoxel.complementary_voxels.remove(best_map_parent)
                    mesovoxel.structural_voxels.append(voxel2)

                    # Copy paint the best map parent onto the voxel2
                    symlist = self.symmetry_df.symlist(voxel2.id, best_map_parent.id)
                    for sym_label in symlist:
                        self.copy_paint(best_map_parent, voxel2, sym_label)

                # If best_map_parent is a structural voxel, add voxel2 to complementary 
                # voxels (will never be None because it's always in mesovoxel)
                else: 
                    print(f"Best map parent is a structural voxel.")
                    mesovoxel.complementary_voxels.append(voxel2)

                # Map paint the best map parent onto the voxel2
                print("\nMap painting all symmetries with best map parent onto voxel2")
                map_symlist = self.symmetry_df.symlist(voxel2.id, best_map_parent.id)
                for sym_label in map_symlist:
                    self.map_paint(best_map_parent, voxel2, sym_label)


                # --- Paint connecting bond between voxel1 and voxel2 --- #
                #TODO: Account for if voxel1 and 2 have any bonds together
                print(f"\nPainting bond between {voxel1.id} and {voxel2.id}...")
                if bond2.color is None:
                    print(f"Painting new bond ({self.n_colors}) between voxel {voxel1.id} and voxel {voxel2.id}")
                    self.n_colors += 1
                    self.paint_bond(bond1, self.n_colors, 'structural')
                    self.paint_bond(bond2, -1*self.n_colors, 'structural')
                else:
                    partner_bond1 = voxel1.has_bond_partner_with(voxel2)
                    if partner_bond1 is not None and partner_bond1.color is not None:
                        print(f"Voxel {voxel2.id} already has a bond with color ({bond2.color}), paint its complement ({-1*bond2.color}) onto voxel {voxel1.id}")
                        self.paint_bond(bond1, partner_bond1.color, 'mapped')
                        self.paint_bond(bond2, -1*partner_bond1.color, 'mapped')
                    else:
                        self.paint_bond(bond1, -1*bond2.color, 'mapped')


                # --- Distribute colors with self-symmetries --- #
                self.paint_self_symmetries(voxel1)
                self.paint_self_symmetries(voxel2)
                self.paint_self_symmetries(best_map_parent)