from typing import Set

from algorithm.Voxel import Voxel
from algorithm.Bond import Bond
from algorithm.Lattice import Lattice
from algorithm.symmetry_df import SymmetryDf
from algorithm.Rotation import Rotater
from algorithm.symmetry.Relation import Relation

class Mesovoxel:
    def __init__(self, lattice: Lattice):
        """
        Mesovoxel data structure, which is comprised a set of structural / complementary 
        voxels. 
            - The structural voxel set is defined clearly by symmetries alone
            - The complementary voxel set starts empty, and we add voxels to it 
              1-by-1 as we paint bonds.
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
    
    def has_voxel(self, voxel) -> bool:
        """
        Check if the voxel is in the mesovoxel.

        Args:
            voxel: int or Voxel object corresponding to the desired voxel to 
                   check if it's in the mesovoxel

        Returns: 
            bool: Whether voxel is in either structural or complementary voxel sets
        """
        voxel_id = self._handle_voxel_type(voxel)
        if voxel_id in self.structural_voxels or voxel_id in self.complementary_voxels:
            return True
        return False
    
    def get_voxel_type(self, voxel) -> str:
        """
        Get the type of the given voxel in the mesovoxel.
        If not present in the mesovoxel, returns None.

        Args:
            voxel: int or Voxel object 
        Returns:
            str or None: Either "structural" or "complementary" based on voxel's set membership,
                         or None if not in either.
        """
        voxel_id = self._handle_voxel_type(voxel)

        if voxel_id in self.structural_voxels:
            return 'structural'
        elif voxel_id in self.complementary_voxels:
            return 'complementary'
        return None

    # --- Internal --- #
    def _handle_voxel_type(self, voxel) -> int:
        """
        Internal function to convert either 'Voxel' object / int --> voxel_id (int)
        """
        if isinstance(voxel, int):
            return voxel
        elif isinstance(voxel, Voxel):
            return voxel.id
        else:
            raise TypeError(f"Invalid argument type for voxel. Expected 'int' or 'Voxel', got '{type(voxel).__name__}'.")
        
    

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
        self.symmetry_df = lattice.symmetry_df
        self.mesovoxel = Mesovoxel(lattice)

        self.rotater = Rotater()

        # Painting sets
        self.painted_voxels = set() # (int)
        self.child_voxels = set() # (int)

        # Count of total # colors (not including complementary) 
        # used to paint the MinDesign
        self.n_colors = 0 

    def str_paint_lattice(self):
        """Phase 1: Paint all structural bonds in lattice"""
        for structural_voxel_id in self.mesovoxel.structural_voxels:
            structural_voxel = self.lattice.get_voxel(structural_voxel_id)
            for direction in structural_voxel.vertex_directions:
                # If vertex already painted, skip
                bond = structural_voxel.get_bond(direction)
                partner_voxel, partner_bond = structural_voxel.get_partner(direction)

                if bond.color is not None or partner_bond.color is not None:
                    continue

                if partner_voxel.id in self.mesovoxel.structural_voxels:
                    # Always paint complementary bond with opposite (negative) color to the original
                    self.n_colors += 1
                    self.paint_bond(bond, self.n_colors, 'structural')
                    self.paint_bond(partner_bond, -1*self.n_colors, 'structural')

                    self.painted_voxels.update((structural_voxel.id, partner_voxel.id)) 
                    print(f'Paint bond with color ({self.n_colors}):\nBetween voxel {structural_voxel.id} ({bond.direction}) and voxel {partner_voxel.id} ({partner_bond.direction})\n')

                    # Then paint self symmetries for both
                    print("Painting self-symmetries for newly painted structural voxels...")
                    self.paint_all_self_symmetries()

    def comp_paint_lattice(self):
        """Phase 2: Paint all complementary bonds in lattice"""

        for voxel1 in self.lattice.voxels:
            for direction in voxel1.vertex_directions:
                bond1 = voxel1.get_bond(direction)
                voxel2, bond2 = voxel1.get_partner(direction)

                if bond1.color is not None and bond2.color is not None:
                    continue

                # Note: Only manipulate painted_voxels in here (for simplicity)
                self.n_colors += 1

                if self.n_colors == 4:
                    return # end early for debug
                
                self.paint_bond(bond=bond1, color=self.n_colors, type="complementary")
                self.paint_bond(bond=bond2, color=-self.n_colors, type="complementary")

                print(f'Paint bond with color ({self.n_colors}):\nBetween voxel {voxel1.id} ({bond1.direction}) and voxel {voxel2.id} ({bond2.direction})\n')


                # Init painted_voxels with voxel1 and 2
                self.painted_voxels.update((voxel1.id, voxel2.id)) 
                
                # Iterative self_symmetry painting:
                # ---
                # We keep removing / adding more voxels to painted_voxels as our 
                # painting affects the adjacent voxels, until further self_symmetry painting 
                # has no effect.
                self.paint_all_self_symmetries()

                # Make sure neither voxel1 nor voxel2 are in child_voxels
                self.child_voxels.discard(voxel1.id)
                self.child_voxels.discard(voxel2.id)

                # Map Painting loop + iterative self_symmetry painting
                # ---
                # Finding best mesoparent and mapping the initial voxel, adding to complementary set if necessary
                mesotype = "complementary" if voxel1.id in self.mesovoxel.structural_voxels else "structural"
                best_mesoparent, sym_label, flip_complementarity = self.find_best_mesoparent(voxel2, mesotype=mesotype)
                
                if best_mesoparent is None:
                    continue

                print(f"Voxel {voxel2.id} has best_mesoparent voxel {best_mesoparent.id}, sym_label {sym_label}, flip_complementarity is {flip_complementarity}")

                # "Map" all bonds of the parent onto the child
                painted_voxels = self.map_paint(child_voxel=voxel2, parent_voxel=best_mesoparent, sym_label=sym_label, flip_complementarity=flip_complementarity)
                self.painted_voxels.update(painted_voxels)
                
                # If our ideal voxel type doesn't yet exist in the mesovoxel, add it 
                # to other set (only happens for complementary)
                if flip_complementarity:
                    print(f"Adding voxel {voxel2.id} to complementary set.")
                    self.mesovoxel.complementary_voxels.add(voxel2.id)
                elif best_mesoparent.id in self.mesovoxel.complementary_voxels:
                    print(f"Adding voxel {voxel2.id} to structural set.")
                    self.mesovoxel.complementary_voxels.remove(best_mesoparent.id)
                    self.mesovoxel.complementary_voxels.add(voxel2.id)

                # Go through all voxels which we painted and find some voxel in the mesovoxel to map onto it
                keep_map_painting = True
                while keep_map_painting:
                    while self.child_voxels:
                        child_voxel_id = self.child_voxels.pop()
                        child_voxel = self.lattice.get_voxel(child_voxel_id)
                        best_mesoparent, sym_label, flip_complementarity = self.find_best_mesoparent(child_voxel)

                        if best_mesoparent is None or sym_label is None or flip_complementarity is None:
                            print(f"Uh oh... no mesoparent found for voxel {child_voxel_id} in loop {self.n_colors}. Why?")
                            continue
                        
                        print(f"Voxel {child_voxel_id} has best_mesoparent voxel {best_mesoparent.id}, sym_label {sym_label}, flip_complementarity is {flip_complementarity}")

                        # Map paint and update painted voxels
                        painted_voxels = self.map_paint(child_voxel=child_voxel, parent_voxel=best_mesoparent, sym_label=sym_label, flip_complementarity=flip_complementarity)
                        self.painted_voxels.update(painted_voxels)
                        self.child_voxels.update(painted_voxels)

                    # Now as a result of map painting we have a new list of voxels we need to paint with self symmetries and check
                    self.paint_all_self_symmetries()
                    if len(self.child_voxels) == 0:
                        keep_map_painting = False
                        break
                
    

    def paint_all_self_symmetries(self) -> None:
        """
        For each voxel in self.painted_voxels, we keep looping through and painting its self symmetries.
        Keep painting and updating painted_voxels until no more changes.
        """
        # Iterative self_symmetry painting:
        # ---
        # We keep removing / adding more voxels to painted_voxels as our 
        # painting affects the adjacent voxels, until further self_symmetry painting 
        # has no effect.
        while self.painted_voxels:
            p_voxel_id = self.painted_voxels.pop()
            p_voxel = self.lattice.get_voxel(p_voxel_id)
            # Paint the affected voxel with its self symmetries
            painted_voxels = self.self_sym_paint(p_voxel)

            # If as a result it paints the voxels around it, update again
            self.painted_voxels.update(painted_voxels)

            # Also, keep track of all non-paint_pair painted_voxels in 
            # child_voxels (to find best mesoparent in next step)
            self.child_voxels.update(painted_voxels)

    def find_best_mesoparent(self, child_voxel: Voxel, mesotype: str=None) -> tuple[Voxel, str, bool]:
        """
        When we map paint, we look for voxels in the mesovoxel which already look like it.
        Mesotype indicates the type of voxel to look for.

        Args:
            voxel2 (Voxel): The voxel2 from comp_paint_lattice loop to find map_parent of
        
        Returns:
            parent_voxel (Voxel)
            sym_label (str)
            flip_complementarity
        """
        flip_complementarity = False

        # First see if we can replace parent with a complementary voxel
        for parent_voxel_id in self.mesovoxel.complementary_voxels:
            parent_voxel = self.lattice.get_voxel(parent_voxel_id)

            # If child_voxel has a bond partner with this parent voxel in the mesovoxel
            # then we flip complementarity ???... logic is a little iffy here
            is_partner = True if child_voxel.has_bond_partner_with(parent_voxel) else False
            print(f"Child voxel {child_voxel.id} is partner with parent voxel {parent_voxel_id}? {is_partner}")
            symlist = self.symmetry_df.symlist(child_voxel.id, parent_voxel_id)
            
            if len(symlist) == 0:
                continue # If two voxels have no symmetries, no way they can be mapped onto each other
            
            # Try all possible symmetry operations to see if we get a valid relation
            for sym_label in symlist:
                rel = Relation.get_voxel_relation(child_voxel, parent_voxel, sym_label)

                print(f"Child voxel {child_voxel.id} and parent voxel {parent_voxel_id} satisfy {rel}")

                if rel == "equal" or rel == "loose equality" or rel == "loose":
                    flip_complementarity = False if not is_partner else True
                    return parent_voxel, sym_label, flip_complementarity
                
                elif rel == "negation" or rel == "loose negation" or rel == "loose":
                    flip_complementarity = True
                    return parent_voxel, sym_label, flip_complementarity
        
        flip_complementarity = True
        for parent_voxel_id in self.mesovoxel.structural_voxels:
            parent_voxel = self.lattice.get_voxel(parent_voxel_id)
            is_partner = True if child_voxel.has_bond_partner_with(parent_voxel) else False
            symlist = self.symmetry_df.symlist(child_voxel.id, parent_voxel_id)
            
            if len(symlist) == 0:
                continue
            
            for sym_label in symlist:
                rel = Relation.get_voxel_relation(child_voxel, parent_voxel, sym_label)
                print(f"Child voxel {child_voxel.id} and parent voxel {parent_voxel_id} satisfy {rel}")
                if rel == "negation" or rel == "loose negation" or rel == "loose":
                    flip_complementarity = True
                    return parent_voxel, sym_label, flip_complementarity
                elif rel == "equal" or rel == "loose equality" or rel == "loose":
                    flip_complementarity = False if not is_partner else True
                    return parent_voxel, sym_label, flip_complementarity
        
        return None, None, None # Ideally should never happen through construction


    def find_best_mesoparent2(self, child_voxel: Voxel, mesotype: str=None) -> tuple[Voxel, str, bool]:
        """
        When we map paint, we look for voxels in the mesovoxel which already look like it.
        Mesotype indicates the type of voxel to look for.

        Args:
            voxel2 (Voxel): The voxel2 from comp_paint_lattice loop to find map_parent of
        
        Returns:
            parent_voxel (Voxel)
            sym_label (str)
            flip_complementarity
        """

        primary_set = self.mesovoxel.structural_voxels if mesotype == "structural" else self.mesovoxel.complementary_voxels
        fallback_set = self.mesovoxel.complementary_voxels  if mesotype == "structural" else self.mesovoxel.structural_voxels

        flip_complementarity = False
        for parent_voxel_id in primary_set:
            parent_voxel = self.lattice.get_voxel(parent_voxel_id)
            bond_partner = child_voxel.has_bond_partner_with(parent_voxel)
            symlist = self.symmetry_df.symlist(child_voxel.id, parent_voxel_id)
            
            if len(symlist) == 0:
                continue
            
            for sym_label in symlist:
                rel = Relation.get_voxel_relation(child_voxel, parent_voxel, sym_label)
                if rel == "equal" or rel == "loose equality" and bond_partner is None:
                    return parent_voxel, sym_label, flip_complementarity
                elif rel == "negation" or rel == "loose negation":
                    flip_complementarity = True
                    return parent_voxel, sym_label, flip_complementarity
        
        flip_complementarity = True
        for parent_voxel_id in fallback_set:
            parent_voxel = self.lattice.get_voxel(parent_voxel_id)
            bond_partner = child_voxel.has_bond_partner_with(parent_voxel)
            symlist = self.symmetry_df.symlist(child_voxel.id, parent_voxel_id)
            
            if len(symlist) == 0:
                continue
            
            for sym_label in symlist:
                rel = Relation.get_voxel_relation(child_voxel, parent_voxel, sym_label)
                if rel == "negation" or rel == "loose negation":
                    return parent_voxel, sym_label, flip_complementarity
                elif rel == "equal" or rel == "loose equality" and bond_partner is None:
                    # flip_complementarity = 
                    return parent_voxel, sym_label, flip_complementarity
        
        return None, None, None # Ideally should never happen through construction
    

    # Painting operations
    def paint_bond(self, bond: Bond, color: int, type: str) -> None:
        """
        Paint certain color / type onto a bond.
        
        Args:
            bond (Bond): The bond object to paint
            color (int): What color to paint it
            type (str): Either "complementary" or "structural" depending on type of bond to paint
        """
        bond.set_color(color)
        bond.set_type(str)

    def map_paint(self, parent_voxel: Voxel, child_voxel: Voxel, sym_label: str, flip_complementarity: bool) -> set[int]:
        """
        Map the bonds of a parent voxel onto the child voxel, with some rotation (sym_label)
        and either flipping the complementarity of all bonds (if flipping complementarity of voxel) or not.

        Returns:
            painted_voxels (set[int])
        """
        # Rotate the bonds of the parent voxel according to the satisfied symmetry operation
        rotated_bond_dict = self.rotater.rotate_voxel(voxel=parent_voxel, rot_label=sym_label)
        
        # And copy them over to the child
        painted_voxels = set()
        comp = -1 if flip_complementarity else 1
        for direction, bond2 in rotated_bond_dict.dict.items():

            bond1 = child_voxel.bond_dict.get_bond(direction)

            # Don't paint if bond1 already painted
            if bond1.color is not None or bond2.color is None:
                continue 

            bond_color = int(bond2.color * comp)
            bond1.set_color(bond_color)
            bond1.set_type(bond2.type)

            # Also paint the partner voxel
            partner_voxel = bond1.get_partner_voxel()
            bond_partner_color = -1*bond_color
            bond1.bond_partner.set_color(bond_partner_color)
            bond1.bond_partner.set_type(bond2.type)

            painted_voxels.add(partner_voxel.id)
            
        return painted_voxels

    def self_sym_paint(self, voxel: Voxel) -> set[int]:
        """Paint the voxel with its own self symmetries.
        
        Args:
            voxel (Voxel): To paint self symmetries of
        
        Returns:
            painted_voxels (set[int]): Set of voxel_ids of all other voxels affected by self sym painting
        """
        symlist = self.symmetry_df.symlist(voxel.id, voxel.id)

        all_painted_voxels = set()
        for sym_label in symlist:
            painted_voxels = self.map_paint(parent_voxel=voxel, child_voxel=voxel, sym_label=sym_label, flip_complementarity=False)
            all_painted_voxels.update(painted_voxels)
        
        return all_painted_voxels
            