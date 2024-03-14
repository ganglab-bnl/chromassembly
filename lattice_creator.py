"""
LatticeCreatorGUI: Tkinter interface for setting lattice dimensions 
and easily creating N-dimensional numpy arrays

You can run this file to test the GUI

@author: Sarah Hong
"""


# Imports
import numpy as np
import tkinter as tk
from tkinter import *
from tkinter import font, ttk

import sv_ttk


class LatticeCreatorGui:
    # TODO: Scrollbar

    def __init__(self):
        """
        Create a lattice creator GUI instance
        """

        self.lattice = None  # The lattice to be returned

        self.ncol = 0
        self.nrow = 0
        self.nlay = 0

        self.root = Tk()
        self.root.wm_title("Lattice Creator")
        self.root.attributes("-topmost", True)

        # Draw frames for setting dimensions and inputting lattice entries
        self.setDimensionFrame = ttk.Frame(master=self.root)
        self.setDimensionFrame.grid(row=0, column=0, sticky='nsew')

        boldFont = font.Font(weight='bold')
        self.setDimTitle = ttk.Label(master=self.setDimensionFrame, text='Set lattice dimensions', font=boldFont)
        self.setDimTitle.grid(row=0, columnspan=2, padx=5, pady=5)

        self.rowLabel = ttk.Label(master=self.setDimensionFrame, text='Number of rows')
        self.rowLabel.grid(row=1, column=0, padx=5, pady=5)
        self.rowEntry = ttk.Entry(master=self.setDimensionFrame)
        self.rowEntry.grid(row=1, column=1, padx=5, pady=5)

        self.colLabel = ttk.Label(master=self.setDimensionFrame, text='Number of columns')
        self.colLabel.grid(row=2, column=0, padx=5, pady=5)
        self.colEntry = ttk.Entry(master=self.setDimensionFrame)
        self.colEntry.grid(row=2, column=1, padx=5, pady=5)

        self.layLabel = ttk.Label(master=self.setDimensionFrame, text='Number of layers')
        self.layLabel.grid(row=3, column=0, padx=5, pady=5)
        self.layEntry = ttk.Entry(master=self.setDimensionFrame)
        self.layEntry.grid(row=3, column=1, padx=5, pady=5)

        self.setDimButton = ttk.Button(master=self.setDimensionFrame, text='Set', command=self.update_inputLatticeFrame)
        self.setDimButton.grid(row=4, columnspan=2, padx=5, pady=5)

        # Input lattice frame widgets
        self.inputLatticeFrame = ttk.Frame(master=self.root)
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
        """ Helper function to raise a frame to the top """
        frame = self.frames[toFrame]
        frame.tkraise()

    def update_inputLatticeFrame(self):
        """
        Update the input lattice frame with the dimensions set by the user
        """
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
            self.layerLabels.append(ttk.Label(master=self.inputLatticeFrame, text='Layer ' + str(i+1)))
            self.layerLabels[i].grid(row=2*i, column=0, padx=5, pady=5)

            # Draw frame to hold inputs for each layer
            self.latticeFrames.append(ttk.Frame(master=self.inputLatticeFrame))
            self.latticeFrames[i].grid(row=(2*i)+1, column=0, padx=5, pady=5)

            for j in range(self.nrow):
                rowEntries = []
                for k in range(self.ncol):
                    entry = ttk.Entry(master=self.latticeFrames[i], width=5)
                    entry.grid(row=j, column=k, padx=5, pady=5)
                    rowEntries.append(entry)
                layerEntries.append(rowEntries)
            self.latticeEntries.append(layerEntries)

        # Buttons to fill lattice
        self.fillZerosButton = ttk.Button(master=self.inputLatticeFrame, text='Fill Zeros', command=lambda: self.fillLattice('zeros'))
        self.fillZerosButton.grid(row=1, column=self.ncol+1, padx=5, pady=5)

        self.fillRandomButton = ttk.Button(master=self.inputLatticeFrame, text='Fill Random', command=lambda: self.fillLattice('random'))
        self.fillRandomButton.grid(row=2, column=self.ncol+1, padx=5, pady=5)

        self.clearButton = ttk.Button(master=self.inputLatticeFrame, text='Clear', command=lambda: self.fillLattice('clear'))
        self.clearButton.grid(row=3, column=self.ncol+1, padx=5, pady=5)

        # Buttons to go baak to setting dimensions and save lattice
        self.redoSetDimButton = ttk.Button(master=self.inputLatticeFrame, text='Back', command=lambda: self.show_frame('setDimension'))
        self.redoSetDimButton.grid(row=2*self.nlay, column=0, padx=5, pady=5)

        self.saveLatticeButton = ttk.Button(master=self.inputLatticeFrame, text='Save Lattice', command=self.saveLattice)
        self.saveLatticeButton.grid(row=(2*self.nlay)+1, column=0, padx=5, pady=5)

        self.show_frame('inputLattice')

    def fillLattice(self, fillType):
        """
        Fill lattice with zeros, random numbers, or clear all entries
        """
        if fillType == 'zeros':
            for i in range(self.nlay):
                for j in range(self.nrow):
                    for k in range(self.ncol):
                        self.latticeEntries[i][j][k].delete(0, END)
                        self.latticeEntries[i][j][k].insert(0, '0')
        elif fillType == 'random':
            for i in range(self.nlay):
                for j in range(self.nrow):
                    for k in range(self.ncol):
                        self.latticeEntries[i][j][k].delete(0, END)
                        self.latticeEntries[i][j][k].insert(0, str(np.random.randint(0, 10)))
        elif fillType == 'clear':
            for i in range(self.nlay):
                for j in range(self.nrow):
                    for k in range(self.ncol):
                        self.latticeEntries[i][j][k].delete(0, END)

    def saveLattice(self):
        """
        Save lattice to self.lattice and close the GUI
        """
        self.lattice = np.zeros((self.nlay, self.nrow, self.ncol))
        for i in range(self.nlay):
            for j in range(self.nrow):
                for k in range(self.ncol):
                    self.lattice[i, j, k] = float(self.latticeEntries[i][j][k].get())
        
        self.root.destroy()
        return self.lattice
    
    def run(self):
        """
        Run the GUI and return the lattice
        """
        sv_ttk.set_theme("dark")
        self.root.mainloop()
        return self.lattice

def main():
    gui = LatticeCreatorGui()
    lattice = gui.run()
    print("The final lattice is:")
    print(lattice)

if __name__ == '__main__':
    main()