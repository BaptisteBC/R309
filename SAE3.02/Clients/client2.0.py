import socket
import sys
import threading

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QApplication, \
    QTextBrowser, QTextEdit, QComboBox, QDialog, QCheckBox


class Identification(QWidget):
    """
    Classe Identification: Première fenêtre à s'afficher au lancement du script client.

    Champs :
        @IP Serveur
        Port
        Identifiant
        Mot de passe

    Boutons:
        Connexion : Lance le script de connexion au serveur utilisant les valeurs des champs @IP Serveur et Port
        Authentification : Lance le script d'authentification avec le serveur en utilisant les valeurs des champs
            Identifiant et Mot de Passe
        Inscription : Lance le script d'inscription avec le serveur en utilisant les valeurs des champs
            Identifiant et Mot de Passe
        Quitter : Envoie un signal de fermeture de la connexion au serveur et ferme l'application
    """
    def __init__(self):
        """
        Création et mise en forme de la fenêtre de tchat
        """
        super().__init__()

        self.window = None
        self.isconnected = False
        self.listen = None
        self.clientsocket = None
        self.stop_sending = threading.Event()

        self.setWindowTitle("Identification")
        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(300, 150)

        self.labServ = QLabel("@IP Serveur")
        self.ipServ = QLineEdit('127.0.0.1')
        self.labPort = QLabel("Port")
        self.portServ = QLineEdit("10000")
        self.labLogin = QLabel("Identifiant")
        self.identifiant = QLineEdit("")
        self.labMdp = QLabel("Mot de passe")
        self.mdp = QLineEdit("")
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
        """
        Vérifie si le client est connecté et si c'est le cas, envoie un signal d'extinction de la connexion au serveur.
        Dans tous les cas ferme l'application proprement.
        """
        if not self.clientsocket:
            QCoreApplication.exit(0)
        elif not self.listen:
            try:
                self.stop_sending.set()
                self.clientsocket.send("bye".encode())
            except ConnectionError:
                self.clientsocket.close()
                QCoreApplication.exit(0)
            else:
                self.clientsocket.close()
                QCoreApplication.exit(0)

        else:
            self.stop_sending.set()
            self.listen.join()
            self.clientsocket.send("bye".encode())
            self.clientsocket.close()
            QCoreApplication.exit(0)

    def connexion(self):
        """
        Script de connexion lancé lorsque le bouton "Connexion" est cliqué.
        Avant de se connexter au serveur, vérifie que les champs requis ne soient pas vides
        """
        if not self.ipServ.text():
            self.reply.append(f"Veuillez indiquer l'adresse IP du serveur.")
        elif not self.portServ.text():
            self.reply.append(f"Veuillez indiquer le port de communication. ")
        elif not self.isconnected:
            try:
                self.clientsocket = socket.socket()
                self.clientsocket.connect((self.ipServ.text(), int(self.portServ.text())))
            except ConnectionError:
                self.reply.append("Erreur de connexion, veuillez réessayer")
            else:
                self.isconnected = True
                reply = self.clientsocket.recv(1024).decode()
                self.reply.setText(reply)
        else:
            pass

    def auth(self):
        """
        Script d'authentification lancé lorsque le bouton "Authentification" est cliqué.
        Vérifie que les champs Identifiant et Mot de Passe ne soient pas vide avant d'envoyer les
        informations au serveur
        """
        if not self.isconnected:
            self.reply.setText("Veuillez vous connecter avant de vous identifier.")
        else:
            identifiant = f"{self.identifiant.text()}"
            mdp = f"{self.mdp.text()}"
            if not identifiant:
                self.reply.append(f"Veuillez indiquer un identifiant.")
            elif not mdp:
                self.reply.append(f"Veuillez indiquer un mot de passe. ")
            else:
                auth = "auth"
                msg = f"{auth}`{identifiant}`{mdp}"
                self.clientsocket.send(msg.encode())

                self.reply.clear()

                reply = self.clientsocket.recv(1024).decode()
                if reply == "auth_OK":
                    self.window = Client(self.clientsocket, identifiant)
                    self.window.show()  # Lancement de la fenêtre de tchat principal
                    self.window.main()  # Lancement de la fonction de démarrage de la fenêtre principale
                    self.close()
                # elif reply == "auth_stop":
                #    print("Trop de tentatives infructueuses, fin de la connexion.")
                #    self.clientsocket.close()
                #    QCoreApplication.exit(0)
                else:
                    self.reply.append(reply)

    def inscription(self):
        """
        Fonction d'inscription du client auprès du serveur lorsque le bouton "Inscription" est cliqué.
        Vérifie que les champs Identifiant et Mot de Passe ne soient pas vide avant d'envoyer les
        informations au serveur
        """
        if not self.isconnected:
            self.reply.setText("Veuillez vous connecter avant de vous identifier.")
        else:
            identifiant = f"{self.identifiant.text()}"
            mdp = f"{self.mdp.text()}"
            if not identifiant:
                self.reply.append(f"Veuillez indiquer un identifiant.")
            elif not mdp:
                self.reply.append(f"Veuillez indiquer un mot de passe. ")
            else:
                inscrire = "inscrire"
                msg = f"{inscrire}`{identifiant}`{mdp}"
                self.clientsocket.send(msg.encode())

                self.reply.clear()

                reply = self.clientsocket.recv(1024).decode()
                if reply == "inscrip_OK":
                    self.window = Client(self.clientsocket, identifiant)
                    self.window.show()
                    self.window.main()
                    self.close()
                else:
                    self.reply.append(reply)


class Client(QWidget):
    """
    Classe Client : Fenêtre de tchat principale permettant de communiquer avec les autres client connectés au serveur.
    Une gestion des serveurs s'effectue grâce au menu déroulant en première ligne de la fenêtre.
    L'envoi des messages s'effectue si l'autorisation est envoyé côté serveur.
    Seuls les messages du serveur dans lequel se trouve le client sont affichés.
    """
    def __init__(self, clientsocket, identifiant):
        super().__init__()

        self.salon = "Général"
        self.perm = False
        self.listen = None
        self.clientsocket = clientsocket
        self.identifiant = identifiant
        self.listeSalons = ['Général', 'Blabla', 'Marketing', 'Informatique', 'Comptabilité']
        self.salonBox = QComboBox()
        self.salonBox.addItems(self.listeSalons)

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

        grid.addWidget(self.salonBox)
        grid.addWidget(self.labMessage)
        grid.addWidget(self.envoi)
        grid.addWidget(self.message)
        grid.addWidget(self.tchat)
        grid.addWidget(self.quitButton)

        self.quitButton.clicked.connect(self.quitter)
        self.envoi.clicked.connect(self.env_msg)
        self.message.returnPressed.connect(self.env_msg)
        self.salonBox.currentTextChanged.connect(self.changeSalon)

    def quitter(self):
        self.clientsocket.send("bye".encode())
        self.flag = True
        self.listen.join()
        self.clientsocket.close()
        QCoreApplication.exit(0)

    def main(self):
        """
        Fonction qui lance la fonction ecoute() dans un thread afin de ne pas empêcher le programme principal
        (interface graphique) de fonctionner.
        """
        self.tchat.setText(f"Bienvenue {self.identifiant} !")

        self.listen = threading.Thread(target=self.ecoute)
        self.listen.start()

    def env_msg(self):
        """
        Fonction d'envoi des messages lorsque le bouton "envoi" est cliqué. Si le salon actuel est différent de
        "Général" alors le client demande la permission d'écrire au serveur.
        """
        salon = self.salon
        message = str(self.message.text())
        if message == "bye":
            self.quitter()
        elif salon == "Général":
            msg = f"{message}`{salon}"
            self.clientsocket.send(msg.encode())
            self.message.clear()
        else:
            msg = f"ask_perm`{salon}"
            self.clientsocket.send(msg.encode())
            if self.perm:
                msg = f"{message}`{salon}"
                self.clientsocket.send(msg.encode())
                self.message.clear()
                self.perm = False

    def ecoute(self):
        """
        Fonction de réception des messages qui sont affichés dans la zone de tchat lorsque le salon du message est le
        même que le salon dans lequel est le client.
        """
        reply = ""
        salon = ""
        while reply != "bye" and reply != "stop" and not self.flag:
            reponse = self.clientsocket.recv(1024).decode()
            recep = reponse.split(sep="`")
            reply = recep[0]
            if len(recep) > 1:
                salon = recep[1]
            if reply == "bye":
                self.clientsocket.send("bye".encode())
                self.flag = True
                self.clientsocket.close()
                QCoreApplication.exit(0)
            elif reply == "perm_OK":
                self.perm = True
            else:
                if salon == self.salon:
                    self.tchat.append(f"{reply}")
                else:
                    pass

    def changeSalon(self):
        """
        Fonction qui récupère le salon actuel dans le menu déroulant dès que celui-ci change.
        Efface les messages de la fenêtre de tchat lorsque le salon change.
        """
        self.salon = self.salonBox.currentText()
        self.tchat.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    identification = Identification()
    identification.show()
    app.exec()
