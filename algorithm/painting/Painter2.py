from typing import Set

from algorithm.lattice.Voxel import Voxel
from algorithm.lattice.Bond import Bond
from algorithm.lattice.Lattice import Lattice
from algorithm.symmetry.Rotation import Rotater
from algorithm.painting.Mesovoxel import Mesovoxel


class Painter:
    def __init__(self, lattice: Lattice, verbose=False):
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

        # Count of total # colors (not including complementary) 
        # used to paint the MinDesign
        self.n_colors = 0 

        # Rotater instance (used for map painting)
        self.rotater = Rotater()
        self.verbose: bool = verbose # If true, prints debugging statements

    def paint_lattice(self):
        """Final callable method to paint the lattice."""
        self.str_paint_lattice()
        self.comp_paint_lattice()

    def str_paint_lattice(self):
        """
        Phase 1: Paint initial set of structural bonds in the lattice.
        Just paint a path of structural bonds connecting all structural voxels
        to each other.
        """

        painted_voxels = set([]) # keep track of all voxels involved for self sym

        for s_voxel_id in self.mesovoxel.structural_voxels:
            s_voxel = self.lattice.get_voxel(s_voxel_id)

            for direction, bond in s_voxel.bond_dict.dict.items():
                partner_voxel, partner_bond = s_voxel.get_partner(direction)

                # --- Paint path of structural bonds ---
                # ensure neither bond is colored yet
                if bond.color is not None or partner_bond.color is not None:
                    continue
                # only want to paint bonds between two structural voxels
                if partner_voxel.type != "structural":
                    continue
                
                # Paint the new bond
                self.n_colors += 1
                self.paint_bond(bond, self.n_colors, 'structural')
                self.paint_bond(partner_bond, -1*self.n_colors, 'structural')

                self.self_sym_paint(s_voxel)
                self.self_sym_paint(partner_voxel)

                # painted_voxels.update((s_voxel_id, partner_voxel.id))

                if self.verbose:
                    print(f"--- PAINT S_BOND ({self.n_colors}) --- \nvoxel_{s_voxel_id} ({bond.direction}) <---> voxel_{partner_voxel.id} ({partner_bond.direction})\n")

        # self symmetry painting
        # while painted_voxels:
        #     voxel = painted_voxels.pop()
        #     self.self_sym_paint(voxel)

    def comp_paint_lattice(self):
        """
        Paint all complementary bonds, slowly adding complementary voxels into the mesovoxel
        until all vertices on the structural voxel set are painted.
        """

        for voxel1_id in self.mesovoxel.structural_voxels:
            voxel1 = self.lattice.get_voxel(voxel1_id)
            for direction1, bond1 in voxel1.bond_dict.dict.items():

                # skip bonds which are already painted
                if bond1.color is not None:
                    continue
                
                # get the voxel which the structural voxel is connected to
                bond2 = bond1.bond_partner
                voxel2 = bond2.voxel

                # check what mesoparent it has
                mesoparents = self.mesovoxel.find_mesoparent(voxel2)
                # unpack
                comp_mp = mesoparents.get("complementary")
                str_mp = mesoparents.get("structural")
            
                self.n_colors += 1

                # if there is a c_voxel in the mesovoxel which looks like voxel2
                if comp_mp:
                    sym = self.lattice.symmetry_df.symlist(voxel2, comp_mp)[0] # take any valid sym
                    self.map_paint(parent=comp_mp, child=voxel2, sym_label=sym) # use it to map
                    
                    # paint the bond
                    if self.verbose:
                        print(f"--- PAINT C_BOND ({self.n_colors}) --- \nvoxel_{voxel1.id} ({bond1.direction}) <---> voxel_{voxel2.id} ({bond2.direction})\n")

                    if bond1.color is None and bond2.color is None:
                        self.paint_bond(bond=bond1, color=self.n_colors, type="complementary")
                        self.paint_bond(bond=bond2, color=-self.n_colors, type="complementary")

                    # paint self symmetries
                    self.self_sym_paint(voxel2)

                    # map the child back onto the parent
                    self.map_paint(parent=voxel2, child=comp_mp, sym_label=sym)

                else: # only a s_voxel is found
                    sym = self.lattice.symmetry_df.symlist(voxel2, str_mp)[0] # take any valid sym
                    self.map_paint(parent=str_mp, child=voxel2, sym_label=sym) # use it to map
                    
                    
                    if bond1.color is None and bond2.color is None:
                        # paint the bond
                        if self.verbose:
                            print(f"--- PAINT C_BOND ({self.n_colors}) --- \nvoxel_{voxel1.id} ({bond1.direction}) <---> voxel_{voxel2.id} ({bond2.direction})\n")

                        self.paint_bond(bond=bond1, color=self.n_colors, type="complementary")
                        self.paint_bond(bond=bond2, color=-self.n_colors, type="complementary")

                        # add the voxel to the complementary set
                        voxel2.set_type("complementary")
                        self.mesovoxel.complementary_voxels.add(voxel2.id)
                    
                    # paint self symmetries
                    self.self_sym_paint(voxel2)

                    # map the child back onto the parent
                    self.map_paint(parent=voxel2, child=str_mp, sym_label=sym)

                    

                

    def self_sym_paint(self, voxel) -> None:
        """Paint a given voxel with all its self symmetries"""
        # handle Voxel and int (voxel.id) instances
        voxel = voxel if isinstance(voxel, Voxel) else self.lattice.get_voxel(voxel)

        if self.verbose:
            print(f"self-sym paint(voxel_{voxel.id})")

        symlist = self.lattice.symmetry_df.symlist(voxel.id, voxel.id)
        for sym_label in symlist:
            self.map_paint(parent=voxel, child=voxel, sym_label=sym_label)

    def map_paint(self, parent, child, sym_label: str):
        """
        Map the bonds of a parent voxel onto the child voxel, with some symmetry operation
        
        Args:
            parent: Voxel or id corresponding to voxel with bond info to map
            child: Voxel or id for voxel as target of mapping
            sym_label (str): Label of rotation to apply to parent voxel before mapping onto child
        """
        parent = parent if isinstance(parent, Voxel) else self.lattice.get_voxel(parent)
        child = child if isinstance(child, Voxel) else self.lattice.get_voxel(child)
        
        if self.verbose:
            print(f"    map_paint(parent_{parent.id} --> child_{child.id}, sym={sym_label})")

        rotated_parent = self.rotater.rotate_voxel(voxel=parent, rot_label=sym_label) # rotated bond_dict object

        # Go through and map each parent bond to the child on its corresponding (rotated) vertex
        for direction, parent_bond in rotated_parent.dict.items():
            child_bond = child.bond_dict.get_bond(direction)

            # don't paint onto already-painted bonds (+ no need to paint None colors)
            if child_bond.color is not None or parent_bond.color is None:
                continue
            
            # Bond color is negated (on c_bonds) if with_negation
            self.paint_bond(child_bond, parent_bond.color, type=parent_bond.type)

            # Also paint the partner voxel (does the updated script need to do this?)
            partner_voxel, bond_partner = child.get_partner(direction)
            self.paint_bond(bond_partner, -1*parent_bond.color, type=parent_bond.type)

    def paint_bond(self, bond: Bond, color: int, type: str) -> None:
        """
        Paint certain color / type onto a bond.
        
        Args:
            bond (Bond): The bond object to paint
            color (int): What color to paint it
            type (str): Either "complementary" or "structural" depending on type of bond to paint
        """
        # if self.verbose:
        #     print(f"\t ---> painting {color} onto voxel {bond.voxel.id}'s bond {bond.get_label()} with type {type} ")
        bond.set_color(color)
        bond.set_type(type)