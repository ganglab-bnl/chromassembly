"""
Class to create new Lattice objects with different binding flexibilities.
"""
from algorithm.Lattice import Lattice
from algorithm.Voxel import Voxel
from algorithm.Bond import Bond
from itertools import combinations

from copy import deepcopy

class BindingFlexibility:

    def __init__(self, lattice: Lattice):
        self.lattice = lattice

    def binding_flexibility_1(self) -> Lattice:
        """
        Create a new Lattice object where all bonds to voxels in the same
        automorphism group are repainted to be the same color.
        """
        # Create a new Lattice object with the same vertices
        lattice = deepcopy(self.lattice)
        for voxel in lattice.voxel_list:
            sym_partners = self.get_sympartners(voxel)
            # if voxel.id == 5:
            #     return lattice
            for sym_group in sym_partners:
                color_dict = {}
                for direction in sym_group:
                    bond = voxel.get_bond(direction)
                    if bond.color not in color_dict:
                        color_dict[bond.color] = [direction]
                    else:
                        color_dict[bond.color].append(direction)
                
                if len(color_dict) <= 1:
                    # All bonds within the group are the same color - continue
                    continue

                # Else, find most frequent color
                max_color = max(color_dict, key=lambda x: len(color_dict[x]))

                # Then go through bonds of other colors and repaint them to max_color
                for color, directions in color_dict.items():
                    if color != max_color:
                        for direction in directions:
                            bond = voxel.get_bond(direction)
                            
                            # Check if the bond can be repainted
                            # valid_color = self.test_valid_paint(bond, max_color)
                            voxel.get_bond(direction).set_color(max_color)
                            voxel.get_bond(direction).bond_partner.set_color(-max_color)
                            # return lattice
                            # bond_complementarity = bond.color // abs(bond.color)
                            # bond_color = abs(max_color) * bond_complementarity

                            # bonds_to_change = voxel.get_bonds_with_color(-bond_color)
                            # bonds_to_change.append(bond)

                            # for bond in bonds_to_change:
                            #     bond.set_color(bond_color)
                            #     bond.bond_partner.set_color(-bond_color)
                
        return lattice
    
    def test_valid_paint(self, bond: Bond, color: int):
        is_not_palindromic = not bond.voxel.is_palindromic(color)
        partner_is_not_palindromic = not bond.bond_partner.voxel.is_palindromic(color)

        is_complementary = bond.bond_partner.color == -1*color
        is_same_color = bond.bond_partner.color == color
        # Both satisfied
        # Adding the color does NOT make both the child and its partner palindromic
        # And satisfies complementarity
        if is_complementary and is_not_palindromic and partner_is_not_palindromic: 
            valid_color = color
        # Neither satisfied
        # Adding the color would make both the child and its partner palindromic
        elif is_same_color and not is_not_palindromic and not partner_is_not_palindromic:
            valid_color = -1*color
        else:
            print("uh oh...")
            valid_color = 0
        # Bad end: Only one or the other is satisfied
        return valid_color

    def get_sympartners(self, voxel) -> list:
        """
        Find all unique sets of partner_voxels on a voxel that have symmetry with each other.
        Return a list of lists, where each sublist contains the directions of the bond to the
        given voxels.
        """
        if isinstance(voxel, int):
            voxel = self.lattice.get_voxel(voxel)

        sym_partners = []

        # Iterate over each bond to create sets of partner voxels
        for _, bond in voxel.bonds.items():
            partner_voxel = bond.get_partner_voxel()
            partner_voxel_id = partner_voxel.id
            added_to_group = False

            # Check if the partner voxel can be added to any existing group
            for sym_group in sym_partners:
                for sym_direction in sym_group:
                    sym_voxel_id = voxel.get_bond(sym_direction).get_partner_voxel().id
                    
                    if sym_voxel_id == partner_voxel_id:
                        continue

                    symlist = self.lattice.SymmetryDf.symlist(sym_voxel_id, partner_voxel_id)

                    # if voxel.id == 4:
                    #     print(f"Voxel {sym_voxel_id} and {partner_voxel_id} have symmetry: {symlist}")

                    if len(symlist) > 0:
                        sym_group.add(bond.get_label())
                        added_to_group = True
                        break

            # If the partner voxel cannot be added to any existing group, create a new group
            if not added_to_group:
                sym_partners.append({bond.get_label()})

        # Convert sets to lists for the final output
        sym_partners = [list(sym_group) for sym_group in sym_partners]

        # Filter out groups with only one bond
        sym_partners = [sym_group for sym_group in sym_partners if len(sym_group) > 1]

        return sym_partners

    