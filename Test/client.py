import socket
import sys
import threading

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QApplication, \
    QTextBrowser, QTextEdit


class Identification(QMainWindow):
    def __init__(self):
        super().__init__()

        self.window = None
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
        self.identifiant = QLineEdit("toto")
        self.labMdp = QLabel("Mot de passe")
        self.mdp = QLineEdit("toto")
        self.reply = QTextEdit()
        self.reply.setReadOnly(True)
        self.connectButton = QPushButton("Connexion")
        self.authButton = QPushButton("Authentification")
        self.inscripButton = QPushButton("Inscription")
        self.quitButton = QPushButton("Quitter")

        self.quitButton.clicked.connect(self.quitter)
        self.connectButton.clicked.connect(self.connexion)
        self.authButton.clicked.connect(self.auth)
        self.inscripButton.clicked.connect(self.inscription)

        grid.addWidget(self.labServ)
        grid.addWidget(self.ipServ)
        grid.addWidget(self.labPort)
        grid.addWidget(self.portServ)
        grid.addWidget(self.connectButton)
        grid.addWidget(self.labLogin)
        grid.addWidget(self.identifiant)
        grid.addWidget(self.labMdp)
        grid.addWidget(self.mdp)
        grid.addWidget(self.authButton)
        grid.addWidget(self.inscripButton)
        grid.addWidget(self.reply)
        grid.addWidget(self.quitButton)

    def quitter(self):
        if not self.clientsocket:
            QCoreApplication.exit(0)
        elif not self.listen:
            self.stop_sending.set()
            self.clientsocket.send("bye".encode())
            self.clientsocket.close()
            QCoreApplication.exit(0)
        else:
            self.stop_sending.set()
            self.listen.join()
            self.clientsocket.send("bye".encode())
            self.clientsocket.close()
            QCoreApplication.exit(0)

    def connexion(self):
        if not self.isconnected:
            self.clientsocket = socket.socket()
            self.clientsocket.connect((self.ipServ.text(), int(self.portServ.text())))
            self.isconnected = True
            reply = self.clientsocket.recv(1024).decode()
            self.reply.setText(reply)
        else:
            pass

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
                self.clientsocket.send("auth".encode())
                self.reply.clear()
                self.clientsocket.send(identifiant.encode())
                self.clientsocket.send(mdp.encode())

                reply = self.clientsocket.recv(1024).decode()
                print(reply)
                if reply == "auth_OK":
                    self.window = Client(self.clientsocket, identifiant)
                    self.window.show()
                    self.window.main()
                    self.close()
                # elif reply == "auth_stop":
                #    print("Trop de tentatives infructueuses, fin de la connexion.")
                #    self.clientsocket.close()
                #    QCoreApplication.exit(0)
                else:
                    self.reply.append(reply)

    def inscription(self):
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
                self.clientsocket.send("inscrire".encode())
                self.reply.clear()
                self.clientsocket.send(identifiant.encode())
                self.clientsocket.send(mdp.encode())

                reply = self.clientsocket.recv(1024).decode()
                print(reply)
                if reply == "inscrip_OK":

                    self.window = Client(self.clientsocket, identifiant)
                    self.window.show()
                    self.window.main()
                    self.close()
                else:
                    self.reply.append(reply)


class Client(QWidget):
    def __init__(self, clientsocket, identifiant):
        super().__init__()

        self.listen = None
        self.clientsocket = clientsocket
        self.identifiant = identifiant

        self.flag = False
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

        self.quitButton.clicked.connect(self.quitter)
        self.envoi.clicked.connect(self.env_msg)
        self.message.returnPressed.connect(self.env_msg)

    def quitter(self):
        self.clientsocket.send("bye".encode())
        self.flag = True
        self.listen.join()
        self.clientsocket.close()
        QCoreApplication.exit(0)

    def main(self):
        self.tchat.setText(f"Bienvenue {self.identifiant} !")
        self.listen = threading.Thread(target=self.ecoute)
        self.listen.start()

    def env_msg(self):
        msg = self.message.text()
        self.clientsocket.send(msg.encode())
        self.tchat.append(f"Moi : {msg}")
        if msg == "bye":
            self.quitter()

    def ecoute(self):
        reply = ""
        while reply != "bye" and reply != "stop" and not self.flag:
            print("yo")
            reply = self.clientsocket.recv(1024).decode()
            self.tchat.append(f"CLient : {reply}")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    identification = Identification()
    identification.show()
    app.exec()
