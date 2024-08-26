# DNA-origami

This algorithm utilizes the symmetry of a 'voxel' containing a particular cargo in 3D space, and combinatorically searches for the minimum number of unique DNA bonds or 'colors' needed to facilitate the self-assembly of such a particle design.

## Installation

Install the requirements `requirements.txt` and the current algorithm can all be run from the jupyter notebook in /notebooks/algorithm.ipynb

## Code structure

### The data structures

1. Create a Lattice structure with Voxel/Bond objects
2. Build out the 'Surroundings'
3. Create SymmetryDf containing all possible truth values of symmetries between any two voxels

### Coloring algorithm

On a high level, the current coloring algorithm is as follows:

"Preprocessing"
1. Define all structurally unique voxels using SymmetryDf
2. Paint all bonds between structural voxels
3. Paint self-symmetries
4. MapPaint the rest of the Lattice

"Main loop"
1. For each Voxel in Lattice -> for each Bond in Voxel
2. Paint that bond and its partner bond (if both are unpainted)
3. Paint both with their self-symmetries
4. MapPaint the rest of the Lattice

The MapPaint function accounts for the following **binding constraints**:

- Bond color complementarity
- No palindromic binding


## GUI application

To test out a simple GUI to create and visualize a lattice (doesn't implement coloring algorithm yet), run the following in the directory root:

```shell
python main.py
```

### Set desired dimensions

<img width="550" alt="Screenshot 2024-07-04 at 2 52 41 AM" src="https://github.com/hyuncat/DNA-origami/assets/114366569/425904d5-8a42-4e1e-9b0a-fbde2c91ddef">


### Visualize

<img width="550" alt="Screenshot 2024-07-04 at 3 13 07 AM" src="https://github.com/hyuncat/DNA-origami/assets/114366569/2a6417be-05c4-47c1-a184-82003608b079">

#### View controls:
- Left button drag / Arrow keys: Rotates the scene around a central point
- Middle button drag: Pan the scene by moving the central “look-at” point within the x-y plane
- Middle button drag + CTRL: Pan the scene by moving the central “look-at” point along the z axis
- Wheel spin: zoom in/out
- Wheel + CTRL(or CMD): change field-of-view angle
