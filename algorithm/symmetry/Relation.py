from algorithm.lattice.Voxel import Voxel
from algorithm.lattice.Bond import Bond, BondDict
from algorithm.symmetry.Rotation import Rotater


class Relation:
    rotater = Rotater()

    def __init__(self):
        pass

    # Level 1: Bond Relations
    def _get_bond_relation(bond1: Bond, bond2: Bond):
        """
        Get the relation between two bonds - options include:
            (1) Equal - Both bonds (c/s) are same color + complementarity
            (2) Loose - At least one None
            (3) Negation - Two bonds (c) are same color, opposing comp
            (4) No relation - Bonds are different abs(color), or s_bonds with opposing complementarity
        (Note that relation order does not matter)
        
        Args:
            bond1: First bond
            bond2: Second bond
        """
        # Case 1: Equal
        if bond1.color == bond2.color:
            return "equal" if  bond1.type == "complementary" and bond2.type == "complementary" else "loose"
            # return "equal"
        
        # Case 2: Loose
        elif bond1.color is None or bond2.color is None:
            return "loose"

        # Case 3: Negation
        elif bond1.color == -bond2.color:
            # Negation can only exist between two complementary bonds
            return "negation" if  bond1.type == "complementary" and bond2.type == "complementary" else "no relation"

        # No relation: Bonds are different colors and not negations on c_bonds
        else: 
            return "no relation" # eg, if two s_bonds are opposing complementarity, they are still no relation
        
    def is_bond_equal(bond1, bond2):
        relation = Relation._get_bond_relation(bond1, bond2)
        return True if relation == "equal" else False
    
    def is_loose(bond1, bond2):
        relation = Relation._get_bond_relation(bond1, bond2)
        return True if relation == "loose" else False
    
    # Level 2: Voxel Relations
    @classmethod
    def get_voxel_relation(cls, voxel1: Voxel, voxel2: Voxel, sym_label=None):
        """
        Get the relation satisfied between two voxels. If sym_label is supplied, 
        rotate voxel1 with the given symmetry (rotation) operation before comparing.

        Args:
            - voxel1 (Voxel): Is rotated if sym_label is provided
            - voxel2 (Voxel): The second voxel to compare voxel1 against
            - syml_label (str): - Name of symmetry operation to transform voxel1 with (optional)
        """

        if voxel1.material != voxel2.material:
            return "no relation"
        
        if sym_label is None:
            bond_dict1 = voxel1.bond_dict
        elif sym_label is not None:
            bond_dict1 = cls.rotater.rotate_voxel(voxel=voxel1, rot_label=sym_label)

        bond_dict2 = voxel2.bond_dict

        # Return the relation between the two bond_dicts
        return Relation.get_bond_dict_relation(bond_dict1, bond_dict2)
    
    # Internal level 2 relation check logic
    def get_bond_dict_relation(bond_dict1: BondDict, bond_dict2: BondDict):
        """ 
        Internal method to get the relation between two voxels. Accepts the BondDicts as input.
        """
        # Summing variables
        equal_count = 0
        loose_count = 0
        negation_count = 0

        for direction, bond1 in bond_dict1.dict.items():
            # Get the bond relation between bonds in the same direction
            bond2 = bond_dict2.get_bond(direction)
            bond_relation = Relation._get_bond_relation(bond1, bond2)

            # Keep sum of all bond relations
            if bond_relation == "equal":
                equal_count += 1
            elif bond_relation == "loose":
                loose_count += 1
            elif bond_relation == "negation":
                negation_count += 1
            
            # If any bonds are "no relation" then the voxels have no relation as well
            else: 
                return "no relation"

        # Check voxel relations based on bond comparisons
        # If any c_bond comparisons are negation, the voxels are negations
        if negation_count >= 1:
            return "negation"
        # If no negations exist but some satisfy equal, then voxels have equality
        elif equal_count >= 1:
            return "equal"
        # Else if all comparisons are loose-loose, then voxels are loose (no info)
        return "loose"

        
    def _get_bond_color(bond):
        if isinstance(bond, int):
            return bond
        elif isinstance(bond, Bond):
            return bond.color
        elif bond is None:
            return None
        else:
            raise TypeError(f"Invalid type for Bond relation. You supplied: {type(bond)}")
        