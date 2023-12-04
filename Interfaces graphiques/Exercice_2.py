import sys

from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QApplication, QLabel, QLineEdit, QPushButton


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        widget = QWidget()
        self.setCentralWidget(widget)
        grid = QGridLayout()
        widget.setLayout(grid)
        self.resize(350, 0)

        self.setWindowTitle("Conversion de Température")

        self.labTemp = QLabel("Température")
        grid.addWidget(self.labTemp, 0, 0)

        self.temp = QLineEdit()
        grid.addWidget(self.temp, 0, 1)

        self.conv = QPushButton("Convertir")
#        self.conv.clicked.connect(self.__actionConvertir)
        grid.addWidget(self.conv, 1, 1)

        self.labConv = QLabel("Conversion")
        grid.addWidget(self.labConv, 2, 0)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
