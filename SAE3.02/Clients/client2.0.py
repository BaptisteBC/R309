import socket
import sys
import threading

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QApplication, \
    QTextBrowser, QTextEdit


class Client(QMainWindow):
    def __init__(self):
        super().__init__()

        self.listen = None
        self.clientsocket = socket.socket()

        self.stop_sending = None
        self.setWindowTitle("Client de tchat")
        widget = QWidget()
        self.setCentralWidget(widget)
        grid = QGridLayout()
        widget.setLayout(grid)
        self.resize(300, 300)

        self.labServ = QLabel("@IP Serveur")
        self.ipServ = QLineEdit('127.0.0.1')
        self.labPort = QLabel("Port")
        self.portServ = QLineEdit("10000")
        self.connectButton = QPushButton("Connexion")
        self.labMessage = QLabel("Votre message :")
        self.message = QLineEdit()
        self.envoi = QPushButton("Envoi")
        self.tchat = QTextEdit()
        self.tchat.setReadOnly(True)
        self.quitButton = QPushButton("Quitter")

        grid.addWidget(self.labServ, 0, 0, 1, 1)
        grid.addWidget(self.ipServ, 0, 1, 1, 1)
        grid.addWidget(self.labPort, 1, 0, 1, 1)
        grid.addWidget(self.portServ, 1, 1, 1, 1)
        grid.addWidget(self.connectButton, 2, 0, 1, 2)
        grid.addWidget(self.labMessage, 3, 0, 1, 1)
        grid.addWidget(self.envoi, 3, 1, 1, 1)
        grid.addWidget(self.message, 4, 0, 1, 2)
        grid.addWidget(self.tchat, 5, 0, 1, 2)
        grid.addWidget(self.quitButton, 6, 0, 1, 2)

        self.quitButton.clicked.connect(self.quitter)
        self.connectButton.clicked.connect(self.connexion)
        self.envoi.clicked.connect(self.envoi_msg)

    def quitter(self):
        self.clientsocket.send("bye".encode())
        self.stop_sending.set()
        self.listen.join()
        self.clientsocket.close()
        QCoreApplication.exit(0)

    def ecoute(self):
        reply = ""
        while reply != "bye" and reply != "stop" and not self.stop_sending.is_set():
            reply = self.clientsocket.recv(1024).decode()
            self.tchat.append(f"CLient : {reply}")

        msg = "bye"
        self.clientsocket.send(msg.encode())
        self.stop_sending.set()

    def connexion(self):
        self.stop_sending = threading.Event()
        self.tchat.append("Tentative de connexion")
        self.clientsocket.connect((self.ipServ.text(), int(self.portServ.text())))
        self.tchat.append("Client connecté")

        self.listen = threading.Thread(target=self.ecoute)
        self.listen.start()

    def envoi_msg(self):
        msg = self.message.text()
        self.tchat.append(f"Moi : {msg}")
        print(f"J'envoie {msg}")
        self.clientsocket.send(msg.encode())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Client()
    window.show()
    app.exec()
