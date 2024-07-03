from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout, QScrollArea

class FillDimensions(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Fill Lattice Dimensions")
        self.layout.addWidget(self.label)

        # Add a scroll area to a container holding the grid
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)

        self.container = QWidget()
        self.gridLayout = QGridLayout()
        self.container.setLayout(self.gridLayout)

        self.scrollArea.setWidget(self.container)
        self.layout.addWidget(self.scrollArea)


    def updateGrid(self, rows, columns, layers):
        # Clear existing widgets in the layout except self.label
        for i in reversed(range(self.gridLayout.count())): 
            layoutItem = self.gridLayout.itemAt(i)
            widget = layoutItem.widget()
            if widget is not None and widget != self.label:
                widget.deleteLater()

        # Adjusted grid creation logic
        currentRow = 0  # Keep track of the current row in the grid layout
        for layer in range(layers):
            # Add a label for each layer at the start of the layer
            layerLabel = QLabel(f"Layer {layer + 1}")
            self.gridLayout.addWidget(layerLabel, currentRow, 0, 1, columns)  # Span the label across all columns
            currentRow += 1  # Move to the next row after adding the layer label

            for row in range(rows):
                for column in range(columns):
                    # Create a QLineEdit for each cell in the layer
                    lineEdit = QLineEdit()
                    self.gridLayout.addWidget(lineEdit, currentRow, column)
                currentRow += 1  # Move to the next row after filling one row of line edits
       
        
        self.gridLayout.setRowStretch(currentRow, 1)

    def clearGrid(self):
        """Clear all text inside the QLineEdit widgets."""
        for i in range(self.gridLayout.count()):
            widget = self.gridLayout.itemAt(i).widget()
            if isinstance(widget, QLineEdit):
                widget.clear()

    def fillZeros(self):
        """Fill all QLineEdit widgets with zeros."""
        for i in range(self.gridLayout.count()):
            widget = self.gridLayout.itemAt(i).widget()
            if isinstance(widget, QLineEdit):
                widget.setText('0')