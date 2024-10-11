from algorithm.Voxel import Voxel
from algorithm.Bond import Bond
from algorithm.Rotation import Rotater

class Relation:

    rotater = Rotater()

    def __init__(self):
        pass

    # Level 1: Bond Relations
    def _get_bond_relation(bond1, bond2):
        color1 = Relation._get_bond_color(bond1)
        color2 = Relation._get_bond_color(bond2)

        # should i have it return an int instead? whatever
        if color1 == color2:
            return "equal"
        elif color1 is None or color2 is None:
            return "loose"
        elif color1 == -color2:
            return "negation"
        else:
            return "no relation"
        
    def is_bond_equal(bond1, bond2):
        relation = Relation._get_bond_relation(bond1, bond2)
        return True if relation == "equal" else False
    
    def is_loose(bond1, bond2):
        relation = Relation._get_bond_relation(bond1, bond2)
        return True if relation == "loose" else False
    
    # Level 2: Voxel Relations
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
        
        # if sym_label is not None:
        #     bond_dict

        bond_dict1 = voxel1.get_bond_dict()
        bond_dict2 = voxel2.get_bond_dict()

        return Relation.get_bond_dict_relation(bond_dict1, bond_dict2)
    

    # Internal level 2 relation check logic
    def get_bond_dict_relation(bond_dict1: dict[tuple[int, int, int], tuple[int, str]], 
                               bond_dict2: dict[tuple[int, int, int], tuple[int, str]]):
        equal_count = 0
        loose_count = 0
        negation_count = 0
        none_count = 0

        for direction, (color1, type1) in bond_dict1.items():
            color2, type2 = bond_dict2.get(direction)
            bond_relation = Relation._get_bond_relation(color1, color2)

            if bond_relation == "equal":
                equal_count += 1
            elif bond_relation == "loose":
                loose_count += 1
            elif bond_relation == "negation":
                negation_count += 1
            else: # Bonds are neither same color, nor abs(color)
                none_count += 1
                return "no relation"

        # Check voxel relations based on bond comparisons
        if equal_count == len(bond_dict1):
            return "equal"
        elif negation_count == len(bond_dict1):
            return "negation"
        elif loose_count > 0 and loose_count + equal_count == len(bond_dict1):
            return "loose equality"
        elif negation_count > 0 and negation_count + loose_count == len(bond_dict1):
            return "loose negation"
        
        # Ideally, those below this line should never happen
        elif loose_count > 0 and equal_count > 0 and negation_count > 0:
            return "loose mixed equality" 
        elif equal_count > 0 and negation_count > 0:
            return "mixed equality"
        
        return "no relation"

        
    def _get_bond_color(bond):
        if isinstance(bond, int):
            return bond
        elif isinstance(bond, Bond):
            return bond.color
        else:
            raise TypeError("Invalid type for Bond relation.")
        
    # def _get_voxel_id(voxel):
    #     if isinstance(voxel, int):
    #         return voxel
    #     elif isinstance(voxel, Voxel):
    #         return voxel.id
