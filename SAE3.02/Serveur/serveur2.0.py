import datetime
import socket
import threading
import mysql.connector


class Serveur:
    def __init__(self, ip='0.0.0.0', port=10000, max_client=5, sql_user='root', sql_mdp='toto', sql_host='127.0.0.1'):
        self.servInput = None
        self.listen = []
        self.client_accept = []
        self.server_socket = socket.socket()
        self.ip = ip
        self.port = port
        self.max_client = max_client
        self.msg = ""
        self.reply = ""
        self.stop_sending = threading.Event()
        self.database = 'coworkapp'
        self.cnx = mysql.connector.connect(user=sql_user, password=sql_mdp, host=sql_host, database=self.database)
        self.liste_client = []
        self.stop_serveur = False
        self.listeSalons = ['Général', 'Blabla', 'Marketing', 'Informatique', 'Comptabilité']

    def main(self):
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
                print(accept)
                self.client_accept.append(accept)
                self.client_accept[client_id].start()
                client_id += 1
            except OSError:
                pass
        self.servInput.join()
        print("Fermeture du serveur")

    def accept(self, conn, address):
        reply = "Client connecté !"
        print(reply, conn)
        conn.send(reply.encode())
        self.auth(conn)

    def auth(self, conn):
        flag = False
        # essais = 3
        while not flag:
            msg = str(conn.recv(1024).decode())
            recep = msg.split(sep="`")
            action = recep[0]
            if action == "auth":
                identifiant = recep[1]
                mdp = recep[2]
                cursor = self.cnx.cursor()
                cursor.execute(f"SELECT * FROM login where Alias like '{identifiant}';")
                results = cursor.fetchall()
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
                    result = results[0]
                    id_client = result[0]
                    if result[2] == mdp:
                        reply = "auth_OK"
                        conn.send(reply.encode())
                        listen = threading.Thread(target=self.ecoute, args=[conn, id_client, identifiant])
                        self.listen.append(listen)
                        listen.start()
                        flag = True
                    else:
                        reply = "Mauvais mot de passe."
                        conn.send(reply.encode())
                        # essais -= 1
                        # if essais == 0:
                        #    print("Trop de tentatives infructueuses")
                        #    conn.send("auth_stop".encode())
                        #    flag = True
            elif action == "inscrire":
                identifiant = recep[1]
                mdp = recep[2]
                cursor = self.cnx.cursor()
                cursor.execute(f"SELECT * FROM login where Alias like '{identifiant}';")
                results = cursor.fetchone()
                if not results:
                    cursor.execute(f"INSERT INTO login VALUES (0, '{identifiant}', '{mdp}');")
                    self.cnx.commit()
                    cursor.execute(f"SELECT idClient FROM login where Alias like '{identifiant}';")
                    results = cursor.fetchone()
                    id_client = results[0]
                    cursor.execute(f"INSERT INTO permissions VALUES ({id_client}, 2, 1)")
                    for i in range(3, 7):
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
                print("Client déconnecté")
                flag = True

    def ecoute(self, conn, id_client, identifiant):
        msg = ""
        salon = ""
        while msg != "bye" and msg != "stop" and not self.stop_serveur and salon != "bye":
            message = str(conn.recv(1024).decode())
            recep = message.split(sep="`")
            msg = recep[0]
            if len(recep) == 2:
                salon = recep[1]
            elif msg == "bye":
                conn.send("bye".encode())
            else:
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
                    print(f"{salon} / {identifiant} : {msg}")
                    self.write_bdd(msg, id_client, identifiant, id_salon, salon)
                    for i in range(len(self.liste_client)):
                        try:
                            self.liste_client[i].send(msg.encode())
                        except ConnectionResetError:
                            pass
                        except ConnectionError:
                            pass
                else:
                    perm_denied = "Vous n'avez pas le droit d'envoyer de message dans ce salon."
                    perm_ask = "perm_ask"
                    reply = f"{perm_denied}`{perm_ask}"
                    conn.send(reply.encode())

        print("Client déconnecté")

    def write_bdd(self, msg, id_client, identifiant, id_salon, salon):
        print(f"Writing : {msg}")
        cursor = self.cnx.cursor()
        date = datetime.datetime.now()
        cursor.execute(
            f"INSERT INTO journal VALUES({id_salon},'{salon}',{id_client},'{identifiant}','{msg}','{date}');")
        self.cnx.commit()
        cursor.close()

    def commandes(self):
        cmd = ""
        while cmd != "kill":
            cmd = str(input("Admin : "))
            if cmd == "kill":
                pass
            else:
                commande = cmd.split(sep=" ")
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
