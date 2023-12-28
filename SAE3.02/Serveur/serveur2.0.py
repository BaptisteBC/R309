#!/usr/bin/env python

from datetime import timedelta, datetime
import socket
import threading
import mysql.connector


class Serveur:
    """
    Classe Serveur : Serveur de tchat permettant la communication de plusieurs clients identifiés

    Fonctions :
        main(): initie la connexion (socket) et lance la fonction commandes() en thread. De plus, cette fonction permet
            de recevoir la connexion des clients puis de lancer la fonction d'authentification auth().
        accept(): fonction lancée dans un thread à la suite de la connexion d'un utilisateur. Cette fonction notifie
            le client de la réussite de la connexion et lance la fonction auth().
        auth(): fonction d'authentification et d'inscription. En fonction du bouton cliqué côté client le programme
            permet soit l'authentification, soit l'inscription du client en intéragissant avec la base de données.
            La possibilité que le client se déconnecte est aussi prise en compte.
        ecoute(): fonction lancée dans un thread qui permet de recevoir tous les messages des client. Cette fonction
            intéragit avec la base de données afin de vérifier les permissions relatives au salons de discussion.
        write_bdd(): fonction lancée à partir de la fonction ecoute(). Cette fonction permet l'écriture des messages
            reçus dans la table "journal" de la base de données.
        commandes(): en parallèle du programme général, permet à l'administrateur de saisir des commandes en ligne
            de commandes afin de bannir définitivement ou temporairement un utilisateur, de le débannir ou de mettre
            fin à la connexion avec tous les clients avant de terminer le script du serveur.

    """

    def __init__(self, ip: str = '0.0.0.0', port: int = 10000, max_client: int = 5, sql_user: str = 'root',
                 sql_mdp: str = 'toto', sql_host: str = '127.0.0.1'):
        """
        :param ip: chaine de caractères prenant en valeur l'adresse IP du serveur. La valeur par défaut est '0.0.0.0',
            soit la machine sur laquelle est lancée ce script.
        :param port: le port d'écoute du serveur. Le port du client et du serveur doivent être identiques pour assurer
            le bon fonctionnement de la communication. Par défaut la valeur du port est 10000.
        :param max_client: maximum de clients pouvant se connecter au serveur. Une fois ce maximum atteint le serveur de tchat
            se ferme. Par défaut la valeur maximum de client est placée à 5.
        :param sql_user: identifiant de connexion au serveur sql
        :param sql_mdp: mot de passe de connexion au serveur sql
        :param sql_host: adresse IP du serveur sql
        """
        self.reponse = None
        self.servInput = None
        self.listen: list = []
        self.client_accept: list = []
        self.liste_client: list = []  # Liste des clients connectés défini par la connexion socket (conn)
        self.clients: list = []  # Liste des clients connectés définis par la connexion socket et leur identifiant
        self.server_socket = socket.socket()  # Création du socket
        self.ip: str = ip
        self.port: int = port
        self.max_client: int = max_client
        self.msg: str = ""
        self.reply: str = ""
        self.stop_sending = threading.Event()
        self.database: str = 'SAE302'
        self.cnx = mysql.connector.connect(user=sql_user, password=sql_mdp, host=sql_host, database=self.database)
        self.stop_serveur: bool = False
        self.listeSalons: list = ['Général', 'Blabla', 'Marketing', 'Informatique', 'Comptabilité']

    def main(self):
        """
        Fonction de lancement du serveur. Lance la fonction commandes() dans un thread et pour chaque nouveau client
        connecté, lance la fonction accept() avec l'argument "conn" qui correspond aux informations du socket client.

        self.servInput : thread de saisie des commandes par l'administrateur
        """
        print("Démarrage du serveur")
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(self.max_client)
        client_id = 0
        self.servInput = threading.Thread(target=self.commandes)
        self.servInput.start()
        while not self.stop_serveur and len(self.liste_client) < self.max_client:
            try:
                conn, address = self.server_socket.accept()
                self.liste_client.append(conn)
                accept = threading.Thread(target=self.accept, args=[conn, address])
                self.client_accept.append(accept)
                self.client_accept[client_id].start()
                client_id += 1
            except OSError:
                pass
        self.servInput.join()
        print("Fermeture du serveur")

    def accept(self, conn, address):
        """
        Fonction de confirmation de la connexion. Cette fonction envoie un message de confirmation au client avant
        de lancer la fonction auth() avec l'argument "conn".
        """
        reply = "Client connecté !"
        conn.send(reply.encode())
        self.auth(conn)

    def auth(self, conn):
        """
        Fonction d'authentification ou d'inscription du client. Trois actions possibles:
            Authentification : Recherche les identifiants reçus dans la base de données et vérifie que l'utilisateur
                ne soit pas banni. Renvoie des messages de confirmation et lance un thread de la fonction ecoute()
                si l'identifiant et le mot de passe correspondent.
            Inscription : Si l'identifiant n'existe pas dans la base de données, alors le serveur l'y enregistre et
                y associe son mot de passe. Le serveur créé aussi les permissions de base pour les salons avant
                de lancer un thread de la fonction ecoute().
            Bye : Si le client décide de se déconnecter avant de s'être authentifié et ferme la connexion, le serveur
                arrête d'essayer d'identifier ce client et cesse la connexion.
        """
        flag = False
        # essais = 3
        while not flag:
            msg = str(conn.recv(1024).decode())
            recep = msg.split(sep="`")
            action = recep[0]
            if action == "auth":  #Authentification
                identifiant = recep[1]
                mdp = recep[2]
                cursor = self.cnx.cursor()
                cursor.execute(f"SELECT * FROM login where Alias like '{identifiant}';")
                results = cursor.fetchone()
                cursor.close()
                if not results:
                    reply = "Identifiant introuvable, réessayez."
                    conn.send(reply.encode())
                    # essais -= 1
                    # if essais == 0:
                    #    reply = "auth_stop"
                    #    print(reply)

                    #    conn.send(reply.encode())
                    #    flag = True
                else:
                    if results[3] == 1:  # results[3] correspond à la colonne "banned" de la table "login"
                        if results[4] is None:  # results[3] correspond à la colonne "kick" de la table "login"
                            reply = "Vous êtes bannis"
                            conn.send(reply.encode())
                        else:
                            date = datetime.now()
                            cursor = self.cnx.cursor()
                            cursor.execute(f"SELECT kick FROM login WHERE Alias like '{identifiant}';")
                            kick_results = cursor.fetchone()
                            date_kick = kick_results[0]
                            calcul = date_kick + timedelta(hours=1)
                            if calcul < date:
                                cursor.execute(
                                    f"UPDATE login SET banned=0, kick=Null WHERE Alias LIKE '{identifiant}';")
                                cursor.close()
                                self.cnx.commit()
                                id_client = results[0]
                                if results[2] == mdp:
                                    reply = "auth_OK"
                                    conn.send(reply.encode())
                                    self.clients.append([identifiant, conn])
                                    listen = threading.Thread(target=self.ecoute, args=[conn, id_client, identifiant])
                                    listen.start()
                                    flag = True
                                else:
                                    reply = "Mauvais mot de passe."
                                    conn.send(reply.encode())
                            else:
                                reply = f"Vous êtes bannis temporairement jusqu'à {calcul}"
                                conn.send(reply.encode())
                    else:
                        id_client = results[0]
                        if results[2] == mdp:
                            reply = "auth_OK"
                            conn.send(reply.encode())
                            self.clients.append([identifiant, conn])
                            listen = threading.Thread(target=self.ecoute, args=[conn, id_client, identifiant])
                            listen.start()
                            # cursor = self.cnx.cursor()
                            # cursor.execute(f"SELECT Alias, message FROM journal INNER "
                            #  "JOIN salons ON salons.idSalon = " f"journal.idSalon WHERE salons.Nom_Salon LIKE "
                            # "'Général';")
                            # results = cursor.fetchall()
                            # for i in results:
                            #   formatage = f"{i[0]} : {i[1]} \n"
                            #   conn.send(formatage.encode()) cursor.close()
                            flag = True
                        else:
                            reply = "Mauvais mot de passe."
                            conn.send(reply.encode())
                            # essais -= 1
                            # if essais == 0:
                            #    print("Trop de tentatives infructueuses")
                            #    conn.send("auth_stop".encode())
                            #    flag = True
            elif action == "inscrire":  # Inscription
                identifiant = recep[1]
                mdp = recep[2]
                cursor = self.cnx.cursor()
                cursor.execute(f"SELECT * FROM login where Alias like '{identifiant}';")
                results = cursor.fetchone()
                if not results:
                    cursor.execute(f"INSERT INTO login(Alias, Mot_de_Passe) VALUES ('{identifiant}', '{mdp}');")
                    self.cnx.commit()
                    cursor.execute(f"SELECT idClient FROM login where Alias like '{identifiant}';")
                    results = cursor.fetchone()
                    id_client = results[0]
                    cursor.execute(f"INSERT INTO permissions VALUES ({id_client}, 1, 1)")
                    for i in range(2, 6):  # Attribution des permissions par défaut
                        cursor.execute(f"INSERT INTO permissions VALUES ({id_client}, {i}, 0)")
                    self.cnx.commit()
                    cursor.close()

                    conn.send("inscrip_OK".encode())

                    listen = threading.Thread(target=self.ecoute, args=[conn, id_client, identifiant])
                    listen.start()
                    flag = True
                else:
                    cursor.close()
                    reply = "Cet identifiant existe déjà, essayez de vous authentifier"
                    conn.send(reply.encode())

            elif action == "bye":
                flag = True

    def ecoute(self, conn, id_client, identifiant):
        """
        Fonction d'écoute du client. Cette fonction reçoit les messages et leurs informations (identifiant, salon) puis
        les vérifie avant de les retransmettre à tous les clients connectés.
        """
        msg = ""
        salon = ""
        while msg != "bye" and msg != "stop" and not self.stop_serveur and salon != "bye":
            message = str(conn.recv(1024).decode())
            recep = message.split(sep="`")
            msg = recep[0]
            if msg == "bye":
                conn.send("bye".encode())
            elif msg == "ask_perm":  # Si le salon est différent de "Général" le client demande la permission d'écrire
                salon = recep[1]
                cursor = self.cnx.cursor()
                cursor.execute("SELECT permissions.idSalon, Permission, permissions.idClient, login.Alias FROM "
                               "permissions INNER JOIN login ON permissions.idClient = login.idClient WHERE "
                               f"login.alias LIKE '{identifiant}';"
                               )
                permissions = cursor.fetchall()
                cursor.execute(f"SELECT idSalon FROM salons WHERE Nom_Salon like '{salon}';")
                salons = cursor.fetchone()
                id_salon = salons[0]
                cursor.close()
                for i in permissions:
                    if i[0] == id_salon:
                        if i[1] == 1:
                            reply = "perm_OK"
                            conn.send(reply.encode())
                        else:
                            reply = ("Vous n'avez pas la permission d'écrire dans ce salon. "
                                     f"Votre demande est transmise à l'administrateur.`{salon}")
                            conn.send(reply.encode())
                    else:
                        pass
            # elif msg == "ask_hist":
            #    msg = conn.recv(1024).decode().split(sep="`")
            #    salon = recep[1]
            #    cursor = self.cnx.cursor()
            #    cursor.execute(f"SELECT Alias, message FROM journal INNER JOIN salons ON salons.idSalon = "
            #                   f"journal.idSalon WHERE salons.Nom_Salon LIKE '{salon}';")
            #    results = cursor.fetchall()
            #    for i in results:
            #        formatage = f"{i[0]} : {i[1]} \n"
            #        conn.send(formatage.encode())
            #    cursor.close()
            else:
                salon = recep[1]
                cursor = self.cnx.cursor()
                cursor.execute(f"SELECT idSalon FROM salons WHERE Nom_Salon LIKE '{salon}';")
                results = cursor.fetchone()
                id_salon = results[0]
                cursor.execute(
                    f"SELECT Permission FROM permissions WHERE idClient LIKE {id_client} AND idSalon LIKE {id_salon};")
                results = cursor.fetchone()
                permission = results[0]
                cursor.close()
                if permission == 1:
                    broadcast = f"{identifiant} : {msg}`{salon}"
                    self.write_bdd(msg, id_client, identifiant, id_salon, salon)
                    for i in range(len(self.liste_client)):
                        try:
                            self.liste_client[i].send(broadcast.encode())
                        except ConnectionResetError:  # Permet de ne pas lever d'erreur si un client a été déconnecté
                            pass
                        except ConnectionError:
                            pass
                else:
                    perm_denied = "Vous n'avez pas le droit d'envoyer de message dans ce salon."
                    perm_ask = "perm_ask"
                    reply = f"{perm_denied}`{perm_ask}"
                    conn.send(reply.encode())

    def write_bdd(self, msg, id_client, identifiant, id_salon, salon):
        """
        Fonction d'enregistrement des messages dans la table "journal" de la base de données
        """
        cursor = self.cnx.cursor()
        date = datetime.now()
        cursor.execute(
            f"INSERT INTO journal VALUES({id_salon},'{salon}',{id_client},'{identifiant}','{msg}','{date}');")
        self.cnx.commit()
        cursor.close()

    def commandes(self):
        """
        Fonction de saisie des commandes par l'administrateur. Les commandes disponibles sont les suivantes :
            kill : met fin au programme de saisie de commandes et envoie un signal de déconnexion aux clients avant
                de terminer le script serveur.
            ban : permet de bannir définitivement l'utilisateur mit en argument
            unban : permet de débannir l'utilisateur mit en argument
            kick : permet de bannir pendant une heure l'utilisateur mit en argument
        """
        cmd = ""
        while cmd != "kill":
            cmd = str(input("Admin : "))
            if cmd == "kill":
                pass
            elif cmd == "yes":
                self.reponse = "yes"
            else:
                commande = cmd.split(sep=" ")
                if len(commande) == 1:
                    pass
                else:
                    user = commande[1]
                    if commande[0] == "ban":
                        cursor = self.cnx.cursor()
                        cursor.execute(f"SELECT * FROM login WHERE Alias LIKE '{user}';")
                        result = cursor.fetchone()
                        if not result:
                            print("L'utilisateur demandé est introuvable")
                            cursor.close()
                        else:
                            cursor.execute(f"UPDATE login SET banned=1 WHERE Alias LIKE '{user}';")
                            self.cnx.commit()
                            cursor.close()
                            for i in self.clients:
                                if i[0] == user:
                                    i[1].send("bye".encode())
                    elif commande[0] == "unban":
                        cursor = self.cnx.cursor()
                        cursor.execute(f"SELECT * FROM login WHERE Alias LIKE '{user}';")
                        result = cursor.fetchone()
                        if not result:
                            print("L'utilisateur demandé est introuvable")
                            cursor.close()
                        else:
                            cursor.execute(f"UPDATE login SET banned=0 WHERE Alias LIKE '{user}';")
                            self.cnx.commit()
                            cursor.close()

                    elif commande[0] == "kick":
                        cursor = self.cnx.cursor()
                        cursor.execute(f"SELECT * FROM login WHERE Alias LIKE '{user}';")
                        result = cursor.fetchone()
                        if not result:
                            print("L'utilisateur demandé est introuvable")
                            cursor.close()
                        else:
                            kick = datetime.now()
                            cursor.execute(f"UPDATE login SET banned='1', kick='{kick}' WHERE Alias LIKE '{user}';")
                            self.cnx.commit()
                            cursor.close()
                            for i in self.clients:
                                if i[0] == user:
                                    i[1].send("bye".encode())

        self.stop_serveur = True
        for i in range(len(self.liste_client)):
            try:
                self.liste_client[i].send("bye".encode())
            except ConnectionResetError:
                pass
            except ConnectionError:
                pass
        self.cnx.close()
        self.server_socket.close()


if __name__ == "__main__":
    serveur = Serveur()
    serveur.main()
