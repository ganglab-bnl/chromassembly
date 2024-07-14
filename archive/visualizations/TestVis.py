import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QLabel, QGridLayout,
                             QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt

class LatticeCreatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Lattice Creator")
        self.lattice = None
        self.isUnitCell = True

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.setDimensionWidget = SetDimensionWidget(self)
        self.inputLatticeWidget = InputLatticeWidget(self)
        
        self.layout.addWidget(self.setDimensionWidget)
        self.layout.addWidget(self.inputLatticeWidget)
        self.inputLatticeWidget.hide()

    def set_dimensions(self, nrow, ncol, nlay):
        self.inputLatticeWidget.configure_grid(nrow, ncol, nlay)
        self.setDimensionWidget.hide()
        self.inputLatticeWidget.show()

    def set_lattice(self, lattice):
        self.lattice = lattice

    def set_isUnitCell(self, isUnitCell):
        self.isUnitCell = isUnitCell

class SetDimensionWidget(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        layout = QGridLayout()
        self.setLayout(layout)

        self.rowLabel = QLabel('Number of rows:')
        self.rowEntry = QLineEdit()
        self.colLabel = QLabel('Number of columns:')
        self.colEntry = QLineEdit()
        self.layLabel = QLabel('Number of layers:')
        self.layEntry = QLineEdit()

        layout.addWidget(self.rowLabel, 0, 0)
        layout.addWidget(self.rowEntry, 0, 1)
        layout.addWidget(self.colLabel, 1, 0)
        layout.addWidget(self.colEntry, 1, 1)
        layout.addWidget(self.layLabel, 2, 0)
        layout.addWidget(self.layEntry, 2, 1)

        self.setButton = QPushButton('Set Dimensions')
        self.setButton.clicked.connect(self.apply_settings)
        layout.addWidget(self.setButton, 3, 0, 1, 2)

    def apply_settings(self):
        nrow = int(self.rowEntry.text())
        ncol = int(self.colEntry.text())
        nlay = int(self.layEntry.text())
        self.controller.set_dimensions(nrow, ncol, nlay)

class InputLatticeWidget(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.grid = QGridLayout()
        self.setLayout(self.grid)

    def configure_grid(self, nrow, ncol, nlay):
        for i in reversed(range(self.grid.count())): 
            self.grid.itemAt(i).widget().setParent(None)

        self.lattice_entries = []
        for lay in range(nlay):
            for row in range(nrow):
                row_entries = []
                for col in range(ncol):
                    entry = QLineEdit()
                    entry.setFixedWidth(50)
                    self.grid.addWidget(entry, row + lay * nrow, col)
                    row_entries.append(entry)
                self.lattice_entries.append(row_entries)

        self.saveButton = QPushButton('Save Lattice')
        self.saveButton.clicked.connect(self.save_lattice)
        self.grid.addWidget(self.saveButton, nlay * nrow + 1, 0, 1, ncol)

    def save_lattice(self):
        nlay = len(self.lattice_entries)
        nrow = len(self.lattice_entries[0])
        ncol = len(self.lattice_entries[0][0])
        lattice = np.zeros((nlay, nrow, ncol))

        for lay in range(nlay):
            for row in range(nrow):
                for col in range(ncol):
                    lattice[lay, row, col] = float(self.lattice_entries[lay][row][col].text())

        self.controller.set_lattice(lattice)
        QMessageBox.information(self, "Lattice Saved", "Your lattice has been saved successfully.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = LatticeCreatorGUI()
    gui.show()
    sys.exit(app.exec())
