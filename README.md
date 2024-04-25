# DNA-origami

Code in-progress for Gang Lab

**Goal:** Find minimum unique voxels and bond colors to create a desired unit cell.

## To test the current code:

To test the code, go to the `origami.ipynb` file and run the cells. You should see a simple GUI pop up, fill in the desired design information and it will save the output as a file containing a numpy array in `lattice.npy`. This is loaded in the next cell (you may have to rerun the cell) and is built out in an interactive visualization using VisPy.

### Set desired dimensions
<img width="250" alt="set dimension" src="https://github.com/hyuncat/DNA-origami/assets/114366569/0af6ad36-ce98-4189-97ef-cec6b288a95a">

### Input values
<img width="250" alt="input desired design" src="https://github.com/hyuncat/DNA-origami/assets/114366569/74d61487-a0a8-49a8-b080-f584e780a191">

### Visualize
<img width="188" alt="vispy" src="https://github.com/hyuncat/DNA-origami/assets/114366569/351abb50-1616-4026-a4bb-2798ca2eb45d">

---

### Installation notes:

You will need to install tkinter if you don't already have it installed, along with pyqt5.
If the vispy library is giving you errors with quartz, go to `vispy/ext/cocoapy.py` and change:

```
quartz = cdll.LoadLibrary(util.find_library('quartz'))
```

to

```
quartz = cdll.LoadLibrary('/System/Library/Frameworks/Quartz.framework/Quartz')
```