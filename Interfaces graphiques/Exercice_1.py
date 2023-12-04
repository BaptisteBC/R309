import sys

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QPushButton, QApplication, QMenu, QLabel, QLineEdit


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        widget = QWidget()
        self.setCentralWidget(widget)
        grid = QGridLayout()
        widget.setLayout(grid)

        self.setWindowTitle("Hello, world !")

        self.__ok = QPushButton("Ok")
        self.__ok.clicked.connect(self.__actionOk)
        grid.addWidget(self.__ok, 3, 0)

        self.__quit = QPushButton("Quitter")
        self.__quit.clicked.connect(self.__actionQuitter)
        grid.addWidget(self.__quit, 4, 0)

        self.__p1 = QLabel("Saisir votre nom")
        grid.addWidget(self.__p1, 0, 0)

        self.__ajoutNom = QLineEdit()
        grid.addWidget(self.__ajoutNom, 1, 0)

        self.__nom = QLabel()
        grid.addWidget(self.__nom, 2, 0)

    def __actionOk(self):
        self.__nom.setText(self.__ajoutNom.text())


    def __actionQuitter(self):
        QCoreApplication.exit(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
