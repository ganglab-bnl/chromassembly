# DNA-origami

Code in-progress for Gang Lab

This algorithm utilizes the symmetry of a 'voxel' containing a particular cargo in 3D space, and combinatorically searches for the minimum number of unique DNA bonds or 'colors' needed to facilitate the self-assembly of such a particle design.

## The algorithm

1. Build out the 'Surroundings'
2. Create SymmetryDf
3. Iteratively color bonds using symmetries

## GUI application

To test out a simple GUI to create and visualize this lattice in 3D space, clone this repo, `/cd` into the root of this directory, and run:

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
