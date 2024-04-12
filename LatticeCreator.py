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
import customtkinter as ctk

import sv_ttk

class LatticeCreatorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Lattice Creator")
        ctk.set_appearance_mode("System") # Set appearance mode to system default :-)

        # Values to be returned
        self.lattice = None
        self.isUnitCell = True

        # Configure the grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Frames
        self.setDimensionFrame = SetDimensionFrame(master=self, controller=self)
        self.inputLatticeFrame = InputLatticeFrame(master=self, controller=self)
        self.frames = {
            'setDimension': self.setDimensionFrame,
            'inputLattice': self.inputLatticeFrame
        }

        self.setDimensionFrame.grid(row=0, column=0, sticky='nsew')
        self.inputLatticeFrame.grid(row=0, column=0, sticky='nsew')

        self.show_frame('setDimension')

        self.mainloop()

    # Helper methods for other classes
    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()

    def set_dimensions(self, nrow, ncol, nlay):
        self.inputLatticeFrame.configure_grid(nrow, ncol, nlay)
        self.show_frame('inputLattice')

    def set_lattice(self, lattice):
        self.lattice = lattice

    def set_isUnitCell(self, isUnitCell):
        self.isUnitCell = isUnitCell
    
    # Run the GUI
    def run(self):
        self.mainloop()
        return self.lattice, self.isUnitCell
    
    def destroy_app(self):
        self.destroy()


class SetDimensionFrame(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master)
        self.controller = controller

        boldFont = ctk.CTkFont(weight='bold')

        self.setDimTitle = ctk.CTkLabel(self, text='Set lattice dimensions', font=boldFont)
        self.setDimTitle.grid(row=0, columnspan=2, padx=10, pady=10)

        self.rowLabel = ctk.CTkLabel(self, text='Number of rows')
        self.rowLabel.grid(row=1, column=0, padx=10, pady=5)
        self.rowEntry = ctk.CTkEntry(self)
        self.rowEntry.grid(row=1, column=1, padx=10, pady=5)

        self.colLabel = ctk.CTkLabel(self, text='Number of columns')
        self.colLabel.grid(row=2, column=0, padx=10, pady=5)
        self.colEntry = ctk.CTkEntry(self)
        self.colEntry.grid(row=2, column=1, padx=10, pady=5)

        self.layLabel = ctk.CTkLabel(self, text='Number of layers')
        self.layLabel.grid(row=3, column=0, padx=10, pady=5)
        self.layEntry = ctk.CTkEntry(self)
        self.layEntry.grid(row=3, column=1, padx=10, pady=5)

        self.setDimButton = ctk.CTkButton(self, text='Set', command=self.apply_settings)
        self.setDimButton.grid(row=4, columnspan=2, padx=10, pady=10)

    def apply_settings(self):
        nrow = int(self.rowEntry.get())
        ncol = int(self.colEntry.get())
        nlay = int(self.layEntry.get())
        self.controller.set_dimensions(nrow, ncol, nlay)


class InputLatticeFrame(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master)
        self.controller = controller

    def configure_grid(self, nrow, ncol, nlay):
        self.nrow = nrow
        self.ncol = ncol
        self.nlay = nlay

        self.lattice_entries = []
        self.layer_labels = []
        self.lattice_frames = []

        for widget in self.winfo_children():
            widget.destroy()

        for lay in range(nlay):
            layer_entries = []

            # Label each layer
            self.layer_labels.append(ctk.CTkLabel(master=self, text='Layer ' + str(lay+1)))
            self.layer_labels[lay].grid(row=2*lay, column=0, padx=5, pady=5)

            # Draw frame to hold inputs for each layer
            self.lattice_frames.append(ctk.CTkFrame(master=self))
            self.lattice_frames[lay].grid(row=(2*lay)+1, column=0, padx=5, pady=5)

            for row in range(nrow):
                entries_row = []
                for col in range(ncol):
                    entry = ctk.CTkEntry(master=self.lattice_frames[lay], width=5)
                    entry.grid(row=row, column=col, padx=5, pady=5)
                    entries_row.append(entry)
                layer_entries.append(entries_row)
            self.lattice_entries.append(layer_entries)

        # Buttons to fill lattice
        self.fillZerosButton = ctk.CTkButton(master=self, text='Fill Zeros', command=lambda: self.fillLattice('zeros'))
        self.fillZerosButton.grid(row=1, column=self.ncol+1, padx=5, pady=5)

        self.fillRandomButton = ctk.CTkButton(master=self, text='Fill Random', command=lambda: self.fillLattice('random'))
        self.fillRandomButton.grid(row=2, column=self.ncol+1, padx=5, pady=5)

        self.clearButton = ctk.CTkButton(master=self, text='Clear', command=lambda: self.fillLattice('clear'))
        self.clearButton.grid(row=3, column=self.ncol+1, padx=5, pady=5)

        self.unitCellIntVar = IntVar(value=1)
        self.unitCellCheckbox = ctk.CTkCheckBox(master=self, text='Unit Cell?', variable=self.unitCellIntVar)
        self.unitCellCheckbox.grid(row=4, column=self.ncol+1, padx=5, pady=5)

        # Buttons to go back to setting dimensions and save lattice
        self.redoSetDimButton = ctk.CTkButton(master=self, text='Back', command=lambda: self.controller.show_frame('setDimension'))
        self.redoSetDimButton.grid(row=2*self.nlay, column=0, padx=5, pady=5)

        self.saveLatticeButton = ctk.CTkButton(master=self, text='Save Lattice', command=self.saveLattice)
        self.saveLatticeButton.grid(row=(2*self.nlay)+1, column=0, padx=5, pady=5)
        

    def fillLattice(self, fillType):
        """
        Fill lattice with zeros, random numbers, or clear all entries
        """
        if fillType == 'zeros':
            for i in range(self.nlay):
                for j in range(self.nrow):
                    for k in range(self.ncol):
                        self.lattice_entries[i][j][k].delete(0, END)
                        self.lattice_entries[i][j][k].insert(0, '0')
        elif fillType == 'random':
            for i in range(self.nlay):
                for j in range(self.nrow):
                    for k in range(self.ncol):
                        self.lattice_entries[i][j][k].delete(0, END)
                        self.lattice_entries[i][j][k].insert(0, str(np.random.randint(0, 5)))
        elif fillType == 'clear':
            for i in range(self.nlay):
                for j in range(self.nrow):
                    for k in range(self.ncol):
                        self.lattice_entries[i][j][k].delete(0, END)

    def saveLattice(self):
        """
        Save lattice to self.lattice and close the GUI
        """
        self.lattice = np.zeros((self.nlay, self.nrow, self.ncol))
        for i in range(self.nlay):
            for j in range(self.nrow):
                for k in range(self.ncol):
                    self.lattice[i, j, k] = float(self.lattice_entries[i][j][k].get())
        
        self.controller.set_lattice(self.lattice)
        self.controller.set_isUnitCell(self.unitCellIntVar.get())

        self.controller.destroy_app()
        return self.lattice # Won't be run lol


if __name__ == '__main__':
    gui = LatticeCreatorGUI()
    lattice, isUnitCell = gui.run()
    print("The final lattice is:")
    print(lattice)
    print(f'Is this a unit cell? {isUnitCell}')
    