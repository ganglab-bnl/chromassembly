from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame
from .SetDimensions import SetDimensions
from .FillDimensions import FillDimensions

class DesignWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.mainLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)

        # --------------------- #
        # Side panel
        # --------------------- #
        self.sidePanelLayout = QVBoxLayout()  # Or QVBoxLayout for vertical arrangement
        self.setDimensionsWidget = SetDimensions()

        # Frame with light grey for visual distinction
        self.sidePanelFrame = QFrame()
        self.sidePanelFrame.setLayout(self.sidePanelLayout)
        self.sidePanelFrame.setFixedWidth(200)  # Set the width of the side panel
        # self.sidePanelFrame.setStyleSheet("background-color: lightgray;")  # Visual distinction

        self.sidePanelLayout.addWidget(self.setDimensionsWidget)
        self.mainLayout.addWidget(self.sidePanelFrame) # Add sidePanel to main layout
        

        # Create a vertical line as a QFrame
        verticalLine = QFrame()
        verticalLine.setFrameShape(QFrame.Shape.VLine) 
        verticalLine.setFrameShadow(QFrame.Shadow.Plain)  
        verticalLine.setStyleSheet("color: lightgray;")  # Set the color of the line
        self.mainLayout.addWidget(verticalLine)

        # --------------------- #
        # Main content
        # --------------------- #
        self.fillDimensionsWidget = FillDimensions()
        self.mainLayout.addWidget(self.fillDimensionsWidget)

        # --------------------- #
        # Signal / slot connections
        # --------------------- #
        # Connect the dimensionsChanged signal to a slot method
        self.setDimensionsWidget.dimensionsChanged.connect(self.fillDimensionsWidget.updateGrid)
        self.setDimensionsWidget.clearLatticeClicked.connect(self.fillDimensionsWidget.clearGrid)
        self.setDimensionsWidget.fillZerosClicked.connect(self.fillDimensionsWidget.fillZeros)
        
        # Initialize fillDimensionsWidget with default values
        self.fillDimensionsWidget.updateGrid(3, 3, 3)

    # Slot method to handle the dimensionsChanged signal
    def updateDimensions(self, rows, columns, layers):
        self.fillDimensionsWidget.updateGrid(rows, columns, layers)