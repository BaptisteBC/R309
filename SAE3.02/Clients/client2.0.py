import socket
import sys
import threading

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QApplication, \
    QTextBrowser, QTextEdit


class Identification(QMainWindow):
    def __init__(self):
        super().__init__()

        self.isconnected = False
        self.listen = None
        self.clientsocket = None
        self.stop_sending = threading.Event()

        self.setWindowTitle("Identification")
        widget = QWidget()
        self.setCentralWidget(widget)
        grid = QGridLayout()
        widget.setLayout(grid)
        self.resize(300, 150)

        self.labServ = QLabel("@IP Serveur")
        self.ipServ = QLineEdit('127.0.0.1')
        self.labPort = QLabel("Port")
        self.portServ = QLineEdit("10000")
        self.labLogin = QLabel("Identifiant")
        self.identifiant = QLineEdit()
        self.labMdp = QLabel("Mot de passe")
        self.mdp = QLineEdit()
        self.reply = QTextEdit()
        self.reply.setReadOnly(True)
        self.connectButton = QPushButton("Connexion")
        self.checkButton = QPushButton("Authentification")
        self.quitButton = QPushButton("Quitter")

        self.quitButton.clicked.connect(self.quitter)
        self.connectButton.clicked.connect(self.connexion)
        self.checkButton.clicked.connect(self.auth)

        grid.addWidget(self.labServ)
        grid.addWidget(self.ipServ)
        grid.addWidget(self.labPort)
        grid.addWidget(self.portServ)
        grid.addWidget(self.connectButton)
        grid.addWidget(self.labLogin)
        grid.addWidget(self.identifiant)
        grid.addWidget(self.labMdp)
        grid.addWidget(self.mdp)
        grid.addWidget(self.checkButton)
        grid.addWidget(self.reply)
        grid.addWidget(self.quitButton)

    def quitter(self):
        self.stop_sending.set()
        self.listen.join()
        self.clientsocket.close()
        QCoreApplication.exit(0)

    def connexion(self):
        self.clientsocket = socket.socket()
        self.clientsocket.connect((self.ipServ.text(), int(self.portServ.text())))
        self.isconnected = True
        reply = self.clientsocket.recv(1024).decode()
        self.reply.setText(reply)

    def auth(self):
        if not self.isconnected:
            self.reply.setText("Veuillez vous connecter avant de vous identifier.")
        else:
            identifiant = f"{self.identifiant.text()}"
            mdp = f"{self.mdp.text()}"
            print(identifiant, mdp)
            if not identifiant:
                self.reply.append(f"Veuillez indiquer un identifiant.")
            elif not mdp:
                self.reply.append(f"Veuillez indiquer un mot de passe. ")
            else:
                self.reply.clear()
                self.clientsocket.send(identifiant.encode())
                self.clientsocket.send(mdp.encode())

                reply = self.clientsocket.recv(1024).decode()
                print(reply)
                if reply == "auth_OK":
                    self.reply.append(f"Bienvenue {identifiant} !")
                    self.window = Client(self.clientsocket)
                    self.window.show()


                elif reply == "auth_stop":
                    print("Trop de tentatives infructueuses, fin de la connexion.")
                    self.clientsocket.close()
                    QCoreApplication.exit(0)
                else:
                    self.reply.append(reply)


class Client(QWidget):
    def __init__(self, clientsocket):
        super().__init__()

        self.listen = None
        self.clientsocket = clientsocket

        self.stop_sending = None
        self.setWindowTitle("Client de tchat")
        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(300, 300)

        self.labMessage = QLabel("Votre message :")
        self.message = QLineEdit()
        self.envoi = QPushButton("Envoi")
        self.tchat = QTextEdit()
        self.tchat.setReadOnly(True)
        self.quitButton = QPushButton("Quitter")

        grid.addWidget(self.labMessage)
        grid.addWidget(self.envoi)
        grid.addWidget(self.message)
        grid.addWidget(self.tchat)
        grid.addWidget(self.quitButton)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    identification = Identification()
    identification.show()
    app.exec()
