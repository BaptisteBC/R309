import sys

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QPushButton, QApplication


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        widget = QWidget()
        self.setCentralWidget(widget)
        grid = QGridLayout()
        widget.setLayout(grid)

        ok = QPushButton("Ok")
        ok.clicked.connect(self.__actionOk)
        grid.addWidget(ok, 0, 0)

        quit = QPushButton("Quitter")
        quit.clicked.connect(self.__actionQuitter)
        grid.addWidget(quit, 0, 1)

        self.setWindowTitle("Hello, world !")

    def __actionOk(self):
        pass

    def __actionQuitter(self):
        QCoreApplication.exit(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()