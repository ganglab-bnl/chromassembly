import numpy as np
import tkinter as tk
from tkinter import *
from tkinter import font
import sv_ttk

class LatticeCreatorGui:

    def __init__(self):

        self.lattice = None  # The lattice to be returned

        self.ncol = 0
        self.nrow = 0
        self.nlay = 0

        self.root = Tk()
        self.root.wm_title("Lattice Creator")
        self.root.attributes("-topmost", True)

        # Draw frames for setting dimensions and inputting lattice entries
        self.setDimensionFrame = tk.Frame(master=self.root)
        self.setDimensionFrame.grid(row=0, column=0, sticky='nsew')

        boldFont = font.Font(weight='bold')
        self.setDimTitle = tk.Label(master=self.setDimensionFrame, text='Set lattice dimensions', font=boldFont)
        self.setDimTitle.grid(row=0, columnspan=2, padx=5, pady=5)

        self.rowLabel = tk.Label(master=self.setDimensionFrame, text='Number of rows')
        self.rowLabel.grid(row=1, column=0, padx=5, pady=5)
        self.rowEntry = tk.Entry(master=self.setDimensionFrame)
        self.rowEntry.grid(row=1, column=1, padx=5, pady=5)

        self.colLabel = tk.Label(master=self.setDimensionFrame, text='Number of columns')
        self.colLabel.grid(row=2, column=0, padx=5, pady=5)
        self.colEntry = tk.Entry(master=self.setDimensionFrame)
        self.colEntry.grid(row=2, column=1, padx=5, pady=5)

        self.layLabel = tk.Label(master=self.setDimensionFrame, text='Number of layers')
        self.layLabel.grid(row=3, column=0, padx=5, pady=5)
        self.layEntry = tk.Entry(master=self.setDimensionFrame)
        self.layEntry.grid(row=3, column=1, padx=5, pady=5)

        self.setDimButton = tk.Button(master=self.setDimensionFrame, text='Set', command=self.update_inputLatticeFrame)
        self.setDimButton.grid(row=4, columnspan=2, padx=5, pady=5)

        # Input lattice frame widgets
        self.inputLatticeFrame = tk.Frame(master=self.root)
        self.inputLatticeFrame.grid(row=0, column=0, sticky='nsew')

        self.latticeEntries = []
        self.latticeFrames = []
        self.layerLabels = []

        # Dictionary of frames
        self.frames = {
            'setDimension': self.setDimensionFrame,
            'inputLattice': self.inputLatticeFrame
        }

        self.show_frame('setDimension') # Start with setDimension frame

    def show_frame(self, toFrame):
        frame = self.frames[toFrame]
        frame.tkraise()

    def update_inputLatticeFrame(self):
        self.nrow = int(self.rowEntry.get())
        self.ncol = int(self.colEntry.get())
        self.nlay = int(self.layEntry.get())

        # Clear previous lattice entries
        self.latticeEntries = []
        self.latticeFrames = []
        self.layerLabels = []

        # Clear previous lattice entries and frames
        for widget in self.inputLatticeFrame.winfo_children():
            widget.destroy()

        for i in range(self.nlay):
            layerEntries = []
            
            # Label each layer
            self.layerLabels.append(tk.Label(master=self.inputLatticeFrame, text='Layer ' + str(i+1)))
            self.layerLabels[i].grid(row=2*i, column=0, padx=5, pady=5)

            # Draw frame to hold inputs for each layer
            self.latticeFrames.append(tk.Frame(master=self.inputLatticeFrame))
            self.latticeFrames[i].grid(row=(2*i)+1, column=0, padx=5, pady=5)

            for j in range(self.nrow):
                rowEntries = []
                for k in range(self.ncol):
                    entry = tk.Entry(master=self.latticeFrames[i], width=5)
                    entry.grid(row=j, column=k, padx=5, pady=5)
                    rowEntries.append(entry)
                layerEntries.append(rowEntries)
            self.latticeEntries.append(layerEntries)

        self.redoSetDimButton = tk.Button(master=self.inputLatticeFrame, text='Back', command=lambda: self.show_frame('setDimension'))
        self.redoSetDimButton.grid(row=2*self.nlay, column=0, padx=5, pady=5)

        self.saveLatticeButton = tk.Button(master=self.inputLatticeFrame, text='Save Lattice', command=self.saveLattice)
        self.saveLatticeButton.grid(row=(2*self.nlay)+1, column=0, padx=5, pady=5)

        self.show_frame('inputLattice')

    def saveLattice(self):
        self.lattice = np.zeros((self.nlay, self.nrow, self.ncol))
        for i in range(self.nlay):
            for j in range(self.nrow):
                for k in range(self.ncol):
                    self.lattice[i, j, k] = float(self.latticeEntries[i][j][k].get())
        
        self.root.destroy()
        return self.lattice
    
    def run(self):
        self.root.mainloop()
        return self.lattice

def main():
    gui = LatticeCreatorGui()
    lattice = gui.run()
    print("The final lattice is:")
    print(lattice)

if __name__ == '__main__':
    main()