from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QFrame
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import Qt

class SetDimensions(QWidget):
    dimensionsChanged = pyqtSignal((int, int, int))
    clearLatticeClicked = pyqtSignal()
    fillZerosClicked = pyqtSignal()
    saveLatticeClicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Widget title
        self.label = QLabel("Set Lattice Dimensions")
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.label)

        # --------------------- #
        # Form layout
        # --------------------- #
        # Hold form layout in container widget (enables vertical alignment w/ stretch)
        self.formContainer = QWidget() 
        self.formLayout = QFormLayout(self.formContainer)

        # Input fields for setting lattice # rows, columns, and layers
        self.input_rows = QLineEdit()
        self.input_columns = QLineEdit()
        self.input_layers = QLineEdit()

        self.formLayout.addRow("Rows:", self.input_rows)
        self.formLayout.addRow("Columns:", self.input_columns)
        self.formLayout.addRow("Layers:", self.input_layers)

        # Form submit button
        self.submit = QPushButton("Update")
        self.submit.clicked.connect(self.update_dimensions)
        self.formLayout.addWidget(self.submit)

        self.layout.addWidget(self.formContainer)
        
        # ----- Horizontal line break -----
        self.lineBreak = QFrame()
        self.lineBreak.setFrameShape(QFrame.Shape.HLine) 
        self.lineBreak.setStyleSheet("color: lightgray;")  # Set the color of the line
        self.layout.addWidget(self.lineBreak)

        # --------------------- #
        # Clear / fill zeros / save lattice buttons
        # --------------------- #
        self.clearLattice = QPushButton("Clear")
        self.clearLattice.clicked.connect(self.clearLatticeClicked.emit)

        self.fillZeros = QPushButton("Fill Zeros")
        self.fillZeros.clicked.connect(self.fillZerosClicked.emit)

        self.saveLattice = QPushButton("Save Lattice")
        self.saveLattice.clicked.connect(self.saveLatticeClicked.emit)

        self.layout.addWidget(self.clearLattice)
        self.layout.addWidget(self.fillZeros)
        self.layout.addWidget(self.saveLattice)

        self.layout.addStretch(1)  # Add a stretch to push everything up

    def update_dimensions(self):
        # Collect values from the QLineEdit widgets
        rows_text = self.input_rows.text()
        columns_text = self.input_columns.text()
        layers_text = self.input_layers.text()

        # Check if any of the fields are empty
        if not rows_text or not columns_text or not layers_text:
            # Optionally, show an error message to the user
            print("All dimensions must be set.")
            return  # Return early if any field is empty

        # Convert text to integers
        rows = int(rows_text)
        columns = int(columns_text)
        layers = int(layers_text)

        # Emit the custom signal with the collected values
        self.dimensionsChanged.emit(rows, columns, layers)