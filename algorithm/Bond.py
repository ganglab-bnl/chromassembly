
class Bond:
    """
    The 'Bond' class represents a bond attached to a particular 
    direction on a Voxel object. The unique information it holds is 
    its bond 'color' and bond type.

    Note: 
    Complementary colors are denoted as a negative version of the original color.
        -> Ex: 2=red, -2=red (complement)
    """
    def __init__(self, voxel: 'Voxel', direction: tuple[float, float, float], 
                 color: int=None, type: str=None, bond_partner: 'Bond'=None):
        """
        Initialize a Bond object. It must be attached to a Voxel object with a 
        particular direction, but the other attributes can be filled in later.
        """
        # Required parameters
        self.voxel = voxel
        self.direction = direction

        # Optional parameters, can be filled in later
        self.color = color 
        self.type = type
        self.bond_partner = bond_partner

    # Setting methods
    def set_color(self, color: int):
        """Set the color of the bond."""
        self.color = color

    def set_bond_partner(self, bond_partner):
        """Set the Bond object which this bond is connected to."""
        self.bond_partner = bond_partner

    def set_type(self, type: str=None):
        """Set bond type to be either a 'structural' or 'mapped' bond."""
        self.type = type

    def get_label(self) -> str:
        """Get a string label for the bond."""
        direction_index = self.voxel.vertex_directions.index(self.direction)
        return self.voxel.vertex_names[direction_index]