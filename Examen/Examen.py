# Lien Github : https://github.com/BaptisteBC/R309/tree/master/Examen

import sys
import socket
import threading

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.conn = None
        self.server_socket = None
        self.setWindowTitle("Le serveur de tchat")
        self.resize(300, 300)

        widget = QWidget()
        self.setCentralWidget(widget)
        grid = QGridLayout()
        widget.setLayout(grid)

        self.labServ = QLabel("Serveur")
        self.ipServ = QLineEdit('0.0.0.0')
        self.labPort = QLabel("Port")
        self.portServ = QLineEdit("10000")  # Défini comme str mais doit être converti en int
        self.labMaxClient = QLabel("Nombre de clients maximum")
        self.maxClient = QLineEdit("5")  # Défini comme str mais doit être converti en int
        self.stopStartButton = QPushButton("Démarrage du serveur")
        self.tchat = QLineEdit()
        self.tchat.setReadOnly(True)
        self.quitButton = QPushButton("Quitter")

        grid.addWidget(self.labServ, 0, 0)
        grid.addWidget(self.ipServ, 0, 1)
        grid.addWidget(self.labPort, 1, 0)
        grid.addWidget(self.portServ, 1, 1)
        grid.addWidget(self.labMaxClient, 2, 0)
        grid.addWidget(self.maxClient, 2, 1)
        grid.addWidget(self.stopStartButton, 3, 0, 1, 2)
        grid.addWidget(self.tchat, 4, 0, 1, 2)
        grid.addWidget(self.quitButton, 5, 0, 1, 2)

        self.quitButton.clicked.connect(self.quitter)
        self.stopStartButton.clicked.connect(self.stopStart)

    def quitter(self):
        QCoreApplication.exit(0)

    def stopStart(self):
        if self.stopStartButton.text() == "Arrêt du serveur":
            self.conn.close()
            self.server_socket.close()
        else:
            self.stopStartButton.setText("Arrêt du serveur")
            self.__demarrage()

    def accept(self):
        self.server_socket.listen(1)
        self.conn, address = self.server_socket.accept()

    def __demarrage(self):
        flag = False
        ip = self.ipServ.text()
        port = self.portServ.text()

        self.server_socket = socket.socket()
        print("Serveur ouvert")
        self.server_socket.bind((ip, int(port)))

        accept = threading.Thread(target=self.accept, args=[self.conn])
        accept.start()

        while not flag:
            host = socket.gethostname()
            self.tchat.setText(f"Client : {host}")
            message = self.conn.recv(1024).decode()
            self.tchat.setText(f"Message reçu : {message}")

            if message == "deco-serveur":
                self.stopStartButton.setText("Démarrage du serveur")
                self.conn.close()
                self.server_socket.close()
                flag = True

        accept.join()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
