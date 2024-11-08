from algorithm.Voxel import Voxel
from algorithm.Bond import Bond
from algorithm.Lattice import Lattice
from algorithm.Relation import Relation
from algorithm.Mesovoxel import Mesovoxel, MVoxel
from algorithm.Rotation import Rotater

from typing import Set


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
        self.mesovoxel = Mesovoxel(lattice, self)

        # Painting sets
        self.painted_voxels: Set[int] = set() # (int)
        self.meso_candidates: Set[int] = set() # (int)

        # Count of total # colors (not including complementary) 
        # used to paint the MinDesign
        self.n_colors = 0 

        # Rotater instance (used for map painting)
        self.rotater = Rotater()


    def str_paint_lattice(self):
        """
        Phase 1: Paint initial set of structural bonds in the lattice

        Note (*) that we only run this on fresh instances of Mesovoxel.
        So we assume voxels are in the mesovoxel iff. they are structural.
        """
        for m_voxel in self.mesovoxel.mvoxels: # (*)
            s_voxel_id = next(iter(m_voxel.maplist))
            s_voxel = self.lattice.get_voxel(s_voxel_id)

            for direction, bond in s_voxel.bond_dict.dict.items():
                partner_voxel, partner_bond = s_voxel.get_partner(direction)

                # Ensure neither bond is colored yet
                if bond.color is not None or partner_bond.color is not None:
                    continue
                # Only want to paint bonds between two structural voxels
                if not self.mesovoxel.contains_voxel(partner_voxel.id): # (*)
                    continue
                
                # Paint a new bond
                self.n_colors += 1
                self.paint_bond(bond, self.n_colors, 'structural')
                self.paint_bond(partner_bond, -1*self.n_colors, 'structural')

                self.painted_voxels.update((s_voxel_id, partner_voxel.id))
                print(f"Paint new s_bond ({self.n_colors}):\nBetween voxel {s_voxel_id} ({bond.direction}) and voxel {partner_voxel.id} ({partner_bond.direction})\n")

                # Iterative self symmetry painting
                while self.painted_voxels:
                    voxel = self.painted_voxels.pop()
                    pv = self.self_sym_paint(voxel)
                    self.painted_voxels.update(pv)

                #TODO: include the newly painted voxels at the end in the s_voxel maplists

    def comp_paint_lattice(self):
        """
        Phase 2: Paint all complementary bonds in the lattice
        """
        for voxel1 in self.lattice.voxels:
            for direction, bond in voxel1.bond_dict.dict.items():
                voxel2, bond2 = voxel1.get_partner(direction)

                # Ensure neither bond is colored yet
                if bond.color is not None or bond2.color is not None:
                    continue

                # Paint a new bond
                self.n_colors += 1
                self.paint_bond(bond, self.n_colors, 'complementary')
                self.paint_bond(bond2, -1*self.n_colors, 'complementary')

                self.painted_voxels.update((voxel1.id, voxel2.id))
                self.meso_candidates.update((voxel1.id, voxel2.id))
                print(f"Paint new c_bond ({self.n_colors}):\nBetween voxel {voxel1.id} ({bond.direction}) and voxel {voxel2.id} ({bond2.direction})\n")

                while True:
                    # Iterative self symmetry painting ("adding info")
                    while self.painted_voxels:
                        voxel = self.painted_voxels.pop()
                        pv = self.self_sym_paint(voxel)
                        self.painted_voxels.update(pv)
                        
                        # Also: Updating list of potential new 'candidate' voxels to add to mesovoxel
                        self.meso_candidates.update(pv) 

                    # Adding new voxels to mesovoxel ("using info to reduce unique origami")
                    while self.meso_candidates:
                        # VOXEL UPDATING LOGIC
                        voxel_id = self.meso_candidates.pop()
                        voxel = self.lattice.get_voxel(voxel_id)

                        mp, with_negation = self.mesovoxel.find_mesoparent(voxel)
                        if mp is None:
                            continue # Skip if no mesoparent found (should never happen)
                        
                        # If we could not find any valid MVoxels aside from this one with negation
                        # and the negation parent has a mesopartner - we know the partner must be the
                        # mesopartner (bottom double-oreo problem)
                        if mp.mesopartner is not None and with_negation:
                            print("Taking the mesoPARTNER as the mesoparent instead...")
                            mp = mp.mesopartner
                            with_negation = False
                        
                        mp_voxel = mp.repr_voxel()
                        print(f"\n--- Found mesoparent {mp_voxel.id} for voxel {voxel_id}, with_negation={with_negation} ---\n")

                        symlist = self.lattice.symmetry_df.symlist(voxel.id, mp_voxel.id)
                        sym_label = symlist[0]
                        pv = self.map_paint(parent=mp_voxel, child=voxel, sym_label=sym_label, with_negation=with_negation)
                        self.painted_voxels.update(pv)
                        self.meso_candidates.update(pv)
                        
                        # Update the rest of equivalent voxels in Mesoparent's maplist with new info
                        # Also returns set of painted voxels to update
                        print(f"Updating voxel information for voxel {mp_voxel.id}'s maplist")
                        pv = mp.update_voxels(voxel, with_negation)

                        # Also update the mesopartner's voxels
                        if mp.mesopartner is not None:

                            mp_partner_voxel = mp.repr_voxel()
                            print(f"Also updating voxel information for MESOPARTNER voxel {mp_partner_voxel.id}'s maplist")
                            with_negation2 = not with_negation
                            pv2 = mp.mesopartner.update_voxels(voxel, with_negation2)
                            pv.update(pv2)

                        self.painted_voxels.update(pv)
                        self.meso_candidates.update(pv)

                        # VOXEL ADDING LOGIC
                        # Don't add the voxel if it's already in the mesovoxel
                        if self.mesovoxel.contains_voxel(voxel):
                            continue

                        if not with_negation:
                            print(f"Adding voxel {voxel.id} to MP voxel {mp_voxel.id}'s maplist {mp.maplist}")
                            mp.maplist.add(voxel.id)
                            self.mesovoxel.voxels[voxel.id] = mp.id

                        # Add a new complementary voxel to the mesovoxel
                        else:
                            mvoxel = MVoxel(
                                id=self.mesovoxel.n_mvoxels(), 
                                voxel=voxel, 
                                type="complementary", 
                                mesovoxel=self.mesovoxel, 
                                mesopartner=mp
                            )
                            self.mesovoxel.mvoxels.append(mvoxel)
                            self.mesovoxel.voxels[voxel_id] = mvoxel.id
                            mp.set_mesopartner(mvoxel)
                            print(f"--- Adding NEW c_voxel to mesovoxel: {mvoxel} ---\n")
                            

                    if len(self.painted_voxels) == 0:
                        break

    # Painting operations
    def paint_bond(self, bond: Bond, color: int, type: str) -> None:
        """
        Paint certain color / type onto a bond.
        
        Args:
            bond (Bond): The bond object to paint
            color (int): What color to paint it
            type (str): Either "complementary" or "structural" depending on type of bond to paint
        """
        print(f"\t ---> painting {color} onto voxel {bond.voxel.id}'s bond {bond.get_label()} with type {type} ")
        bond.set_color(color)
        bond.set_type(type)

    def map_paint(self, parent, child, sym_label: str, with_negation: bool) -> set[int]:
        """
        Map the bonds of a parent voxel onto the child voxel, with some rotation (sym_label).
        If with_negation is True, then we flip the complementarity of all c_bonds

        Args:
            parent: Voxel/int, of the 'parent' voxel to map onto the child
            child: Voxel/int, of the 'child' voxel to have new bonds colored onto
            sym_label: Name of transformation to apply to parent before mapping onto child
            with_negation: Whether to flip complementarity of c_bonds or not

        Returns:
            painted_voxels: A set of voxel ids which were also painted in the process
        """
        parent = parent if isinstance(parent, Voxel) else self.lattice.get_voxel(parent)
        child = child if isinstance(child, Voxel) else self.lattice.get_voxel(child)

        # Rotate the bonds of the parent voxel according to the satisfied symmetry operation
        rotated_bond_dict = self.rotater.rotate_voxel(voxel=parent, rot_label=sym_label)

        # And copy them over to the child
        painted_voxels = set()
        comp = -1 if with_negation else 1

        for direction, parent_bond in rotated_bond_dict.dict.items():
            child_bond = child.bond_dict.get_bond(direction)

            # Don't paint onto already-painted bonds (+ no need to paint None colors)
            if child_bond.color is not None or parent_bond.color is None:
                continue
            
            # Bond color is negated (on c_bonds) if with_negation
            bond_color = int(parent_bond.color * comp) if parent_bond.type == "complementary" else parent_bond.color
            self.paint_bond(child_bond, bond_color, type=parent_bond.type)

            # Also paint the partner voxel
            partner_voxel, bond_partner = child.get_partner(direction)
            bond_partner_color = -1*bond_color
            self.paint_bond(bond_partner, bond_partner_color, type=parent_bond.type)

            painted_voxels.add(partner_voxel.id)
        
        return painted_voxels

    def self_sym_paint(self, voxel) -> set[int]:
        """
        Map paint all of a voxel's self symmetries onto itself. 

        Returns painted_voxels, a set of all other voxels in the lattice 
        which are also painted as a result of the self symmetry painting.
        """
        voxel = voxel if isinstance(voxel, Voxel) else self.lattice.get_voxel(voxel)
        symlist = self.lattice.symmetry_df.symlist(voxel.id, voxel.id)

        painted_voxels = set()
        for sym_label in symlist:
            pv = self.map_paint(parent=voxel, child=voxel, sym_label=sym_label, with_negation=False)
            painted_voxels.update(pv)

        return painted_voxels
    
        