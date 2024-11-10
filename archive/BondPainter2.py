import numpy as np
import pandas as pd
from typing import Set
import copy

from .Voxel import Voxel
from .Bond import Bond
from .Lattice import Lattice
from .Surroundings import Surroundings
from .symmetry_df import SymmetryDf
from .Rotation import VoxelRotater

class Mesovoxel:
    def __init__(self, lattice: Lattice):
        """
        Mesovoxel to manipulate a set of structural / complementary voxels as we paint.
        """
        self.structural_voxels = self.init_structural_voxels(lattice, lattice.symmetry_df)
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
    def __init__(self, lattice: Lattice):
        """
        Manager class for coloring bonds between voxels in a lattice.
        """
        self.lattice = lattice
        self.symmetry_df = lattice.symmetry_df
        self.voxel_rotater = VoxelRotater()
        self.mesovoxel = Mesovoxel(lattice)

        self.n_colors = 0 # Count of total # colors (not including complementary) used to paint the MinDesign
    
    def paint_lattice(self):
        """Final coloring algorithm to paint the lattice."""
        print("Initializing the mesovoxel...")
        self.init_mesopaint()
        print("Coloring the lattice...")
        self.main_loop()
        self.lattice.n_colors = self.n_colors
        print("Done!")
    
    # --- Internal --- #

    def init_mesopaint(self):
        """
        Paint all bonds between structural voxels in the Mesovoxel
        """
        # print("INITIAL MESOVOXEL PAINTING\n---")
        # print("Painting all bonds between two structural voxels...")

        painted_s_voxels = set()
        for structural_voxel_id in self.mesovoxel.structural_voxels:
            structural_voxel = self.lattice.get_voxel(structural_voxel_id)
            for direction in structural_voxel.vertex_directions:

                # If vertex already painted, skip
                bond = structural_voxel.get_bond(direction)
                partner_voxel, partner_bond = structural_voxel.get_partner(direction)
                paint_set = frozenset([structural_voxel.id, partner_voxel.id])

                if partner_bond.color is not None or partner_bond.color is not None:
                    continue
                if paint_set in painted_s_voxels:
                    continue

                if partner_voxel.id in self.mesovoxel.structural_voxels:
                    # Always paint complementary bond with opposite (negative) color to the original
                    self.n_colors += 1
                    self.paint_bond(bond, self.n_colors, 'structural')
                    self.paint_bond(partner_bond, -1*self.n_colors, 'structural')

                    self.paint_self_symmetries(structural_voxel)
                    self.paint_self_symmetries(partner_voxel)

                    self.swap_paint_lattice(structural_voxel)
                    self.swap_paint_lattice(partner_voxel)

                    self.map_paint_lattice(structural_voxel)
                    self.map_paint_lattice(partner_voxel)
                    
                    painted_s_voxels.add(paint_set)
                    # print(f'Paint bond with color ({self.n_colors}):\nBetween voxel {structural_voxel.id} ({bond.direction}) and voxel {partner_voxel.id} ({partner_bond.direction})\n')

        # count = 1
        # for structural_voxel_id in self.mesovoxel.structural_voxels:
        #     structural_voxel = self.lattice.get_voxel(structural_voxel_id) 

        #     # Then paint self symmetries for both
        #     # print("Painting self-symmetries for newly painted structural voxels...")
            
        #     # self.paint_self_symmetries(partner_voxel)
        #     self.swap_paint_lattice(structural_voxel)
        #     break
            # self.map_paint_lattice(structural_voxel)
            # count += 1
            # if count >= 3:
            #     break
            # Then map_paint the lattice with both voxels
            # print("Map painting the lattice with newly painted structural voxels...")


    def main_loop(self):
        """
        Main loop to paint the entire lattice with 3 distinct steps per loop:
        1. Paint a new bond between two voxels
        2. Paint self-symmetries for both voxels
        3. Map paint the lattice with both voxels
        """
        for voxel1 in self.lattice.voxels:
            # if voxel1.id == 1:
            #     return
            for direction in voxel1.vertex_directions:
                bond1 = voxel1.get_bond(direction)
                voxel2, bond2 = voxel1.get_partner(direction)

                if bond1.color is not None and bond2.color is not None:
                    continue
                    
                # --- Paint connecting bond between voxel1 and voxel2 --- #
                # print(f"Paint NEW bond ({self.n_colors})between {voxel1.id} and {voxel2.id}...\n---")
                self.n_colors += 1
                self.paint_bond(bond1, self.n_colors, 'complementary')
                self.paint_bond(bond2, -1*self.n_colors, 'complementary')

                # Paint self-symmetries for both voxels
                self.paint_self_symmetries(voxel1)
                self.paint_self_symmetries(voxel2)

                # # Swap paint the lattice
                self.swap_paint_lattice(voxel1)
                self.swap_paint_lattice(voxel2)

                # Map paint the lattice with both voxels
                self.map_paint_lattice(voxel1)
                self.map_paint_lattice(voxel2)

                # return

    def paint_bond(self, bond: Bond, color: int, type: str=None) -> None:
        """
        Paint the bond on a given vertex with a given color.
        Optionally, denote whether it is a structural or mapped bond.
        """
        bond.set_color(color)
        if type is not None:
            bond.set_type(type)

    def paint_self_symmetries(self, voxel: Voxel):
        """
        Paint all self-symmetries for a given voxel.
        """
        self_symlist = self.symmetry_df.symlist(voxel.id, voxel.id)
        # print(f'\nPAINT SELF SYMMETRIES: Voxel {voxel.id}: {self_symlist}')
        for sym_label in self_symlist:
            if sym_label == "translation":
                continue
            self.map_paint(voxel, voxel, sym_label)

    def map_paint(self, parent_voxel: Voxel, child_voxel: Voxel, sym_label: str) -> None:
        """
        Maps all bond colors from a parent voxel onto a child voxel as a result of a
        particular symmetry operation. Incorporates palindromic and complementarity
        binding rules.
        
        @param:
            - parent_voxel: Voxel to -> apply symmetry operation -> map onto child
            - child_voxel: Voxel to receive the mapped bond colors
            - sym_label: name of the symmetry operation to apply
        """
        rotated_bond_dict = self.voxel_rotater.rotate_voxel_bonds(parent_voxel, sym_label)
        new_bond_dict = {}
        for rot_direction, rot_bond_color_type in rotated_bond_dict.items():

            rot_bond_color, rot_bond_type = rot_bond_color_type

            child_bond = child_voxel.get_bond(rot_direction)
            # Don't MapPaint onto already painted bonds
            if child_bond.color is not None:
                continue
            # Don't MapPaint a None color onto the child
            if rot_bond_color is None:
                continue

            # If child_bond's partner is uncolored, only check palindromic on the child
            map_color = None
            is_not_palindromic = not child_voxel.is_palindromic(rot_bond_color)

            partner_voxel, partner_bond = child_voxel.get_partner(rot_direction)
            partner_is_not_palindromic = not partner_voxel.is_palindromic(-1*rot_bond_color)

            if child_bond.bond_partner.color is None:
                if is_not_palindromic and partner_is_not_palindromic:
                    map_color = rot_bond_color
                elif not is_not_palindromic and not partner_is_not_palindromic:
                    map_color = -1*rot_bond_color
                else:
                    return

            # If child_bond's partner is colored, check both palindromic and complementarity
            else:
                is_complementary = child_bond.bond_partner.color == -1*rot_bond_color
                is_same_color = child_bond.bond_partner.color == rot_bond_color
                # Both satisfied
                # Adding the color does NOT make both the child and its partner palindromic
                # And satisfies complementarity
                if is_complementary and is_not_palindromic and partner_is_not_palindromic: 
                    map_color = rot_bond_color
                # Neither satisfied
                # Adding the color would make both the child and its partner palindromic
                elif is_same_color and not is_not_palindromic and not partner_is_not_palindromic:
                    map_color = -1*rot_bond_color
                # Bad end: Only one or the other is satisfied
                else: 
                    # If only one of the conditions is satisfied, don't map paint
                    # the entire voxel
                    # (avoids infinite loop)
                    return
            
            # Check if color-to-map already exists on the child_voxel
            # child_bond_type = child_voxel.get_bond_type(map_color)
            # if child_bond_type is None: # Color does not exist
            #     child_bond_type = 'mapped'

            # new_bond_dict[rot_direction] = (map_color, child_bond_type)

            # Note: Is the above necessary? what if we just did based on parent bond type?
            new_bond_dict[rot_direction] = (map_color, rot_bond_type)

        # If we never reached the bad end, set the child_voxel to the mapped copy
        for direction, color_type in new_bond_dict.items():
            color, type = color_type
            child_voxel.bonds[direction].color = color
            child_voxel.bonds[direction].type = type
            partner_bond = child_voxel.bonds[direction].bond_partner
            partner_bond.color = -1*color
            partner_bond.type = type


    def map_paint_lattice(self, parent_voxel: Voxel):
        """For each other_voxel in the lattice that is not itself, map_paints 
        its symmetries (those valid symlist items) onto the other_voxel"""
        for child_voxel_id, symlist in self.lattice.symmetry_df.partner_symdict(parent_voxel.id).items():
            child_voxel = self.lattice.get_voxel(child_voxel_id)
            if parent_voxel.id == child_voxel.id:
                continue

            # if child is a direct partner of parent, flip complementarity when map_painting
            if parent_voxel.has_bond_partner_with(child_voxel.id) is not None:
                flipped_voxel = copy.deepcopy(parent_voxel)
                # flipped_voxel.bonds = flipped_voxel.flip_complementarity(list(all_parent_colors))
                for _, bond in flipped_voxel.bonds.items():
                    if bond.color is not None:
                        bond.color = -1*bond.color
                
                for sym_label in symlist:
                    self.map_paint(flipped_voxel, child_voxel, sym_label)
            # normally just map paint dirrectly
            else:
                for sym_label in symlist:
                    self.map_paint(parent_voxel, child_voxel, sym_label)

            # symlist = self.symmetry_df.symlist(parent_voxel.id, child_voxel.id)

            # we need to choose the best symmetry to map paint
            

    def swap_paint_lattice(self, parent_voxel: Voxel):
        for symvoxel_id in self.lattice.symmetry_df.partner_symdict(parent_voxel.id):
            # Swap painting constraints
            if parent_voxel.id == symvoxel_id:
                continue # don't swap the parent with itself
            if parent_voxel.has_bond_partner_with(symvoxel_id) is not None:
                continue # don't swap paint direct partners of the parent

            symvoxel = self.lattice.get_voxel(symvoxel_id)
            symlist = self.symmetry_df.symlist(parent_voxel.id, symvoxel_id)

            best_rot = self.voxel_rotater.find_best_rotation(parent_voxel, symvoxel, symlist)
            if best_rot is None:
                continue

            #TODO: Account for bond type
            rot_bond_dict = self.voxel_rotater.rotate_voxel_bonds(parent_voxel, best_rot)
            for direction, rot_bond_color_type in rot_bond_dict.items():

                rot_bond_color, rot_bond_type = rot_bond_color_type

                child_bond = symvoxel.get_bond(direction)
                child_bond.color = rot_bond_color
                child_bond.type = rot_bond_type

                if rot_bond_color is not None:
                    color = -1*rot_bond_color
                else:
                    color = None
                child_partner_bond = child_bond.bond_partner
                child_partner_bond.color = color
                child_partner_bond.type = rot_bond_type
                
    # archived methods         
    # def map_paint(self, parent_voxel: Voxel, child_voxel: Voxel, sym_label: str) -> None:
    #     """
    #     Maps all bond colors from a parent voxel onto a child voxel as a result of a
    #     particular symmetry operation. Incorporates palindromic and complementarity
    #     binding rules.
        
    #     @param:
    #         - parent_voxel: Voxel to -> apply symmetry operation -> map onto child
    #         - child_voxel: Voxel to receive the mapped bond colors
    #         - sym_label: name of the symmetry operation to apply
    #     """

    #     rotated_parent_voxel = self.voxel_rotater.rotate_voxel(parent_voxel, sym_label)
    #     child_voxel_copy = copy.deepcopy(child_voxel)

    #     for direction, parent_bond in rotated_parent_voxel.bonds.items():

    #         if parent_bond.color is None:
    #             continue
            
    #         child_bond_copy = child_voxel_copy.get_bond(direction)
    #         # Don't MapPaint onto already painted bonds
    #         if child_bond_copy.color is not None:
    #             continue
            
    #         # If child_bond's partner is uncolored, only check palindromic
    #         map_color = None
    #         is_not_palindromic = not child_voxel.is_palindromic(parent_bond.color)
            
    #         if child_bond_copy.bond_partner.color is None:
    #             if is_not_palindromic:
    #                 map_color = parent_bond.color
    #             else:
    #                 map_color = -1*parent_bond.color

    #         # If child_bond's partner is colored, check both palindromic and complementarity
    #         else:
    #             is_complementary = child_bond_copy.bond_partner.color == -1*parent_bond.color
    #             # Both satisfied
    #             if is_complementary and is_not_palindromic: 
    #                 map_color = parent_bond.color
    #             # Neither satisfied
    #             elif not is_complementary and not is_not_palindromic:
    #                 map_color = -1*parent_bond.color
    #             # Bad end: Only one or the other is satisfied
    #             else: 
    #                 # If only one of the conditions is satisfied, don't map paint
    #                 # the entire voxel
    #                 # (avoids infinite loop)
    #                 return
            
    #         # Check if color-to-map already exists on the child_voxel
    #         child_bond_type = child_voxel.get_bond_type(map_color)
    #         if child_bond_type is None:
    #             child_bond_type = 'mapped'
    #         # print(f'MapPaint {map_color} from parent voxel{parent_voxel.id} {parent_bond.get_label()} --> child voxel{child_voxel.id} {child_bond_copy.get_label()} with type {child_bond_type}')

    #         self.paint_bond(child_bond_copy, map_color, child_bond_type)
    #         # self.paint_bond(child_bond.bond_partner, -1*parent_bond.color, 'mapped')
    #         # print(f' ---> MapBond ({parent_bond.color}) from parent_bond {parent_bond.get_label()} --> child_bond {child_bond_copy.get_label()}')

    #     # If we never reached the bad end, set the child_voxel to the mapped copy
    #     for direction, mapped_bond in child_voxel_copy.bonds.items():
    #         child_voxel.bonds[direction].color = mapped_bond.color
    #         child_voxel.bonds[direction].type = mapped_bond.type

    #     # print("\n")

    