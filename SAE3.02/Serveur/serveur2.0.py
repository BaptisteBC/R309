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
            action = conn.recv(1024).decode()
            if action == "auth":
                print(action)
                identifiant = conn.recv(1024).decode()
                mdp = conn.recv(1024).decode()
                print(identifiant, mdp)
                cursor = self.cnx.cursor()
                cursor.execute(f"SELECT * FROM login where Alias like '{identifiant}';")
                results = cursor.fetchall()
                cursor.close()
                if not results:
                    reply = "Identifiant introuvable, réessayez."
                    print(reply)
                    conn.send(reply.encode())
                    # essais -= 1
                    # if essais == 0:
                    #    reply = "auth_stop"
                    #    print(reply)

                    #    conn.send(reply.encode())
                    #    flag = True
                else:
                    result = results[0]
                    print(result)
                    id_client = result[0]
                    if result[2] == mdp:
                        reply = "auth_OK"
                        conn.send(reply.encode())
                        print(reply)
                        listen = threading.Thread(target=self.ecoute, args=[conn, id_client, identifiant])
                        self.listen.append(listen)
                        listen.start()
                        flag = True
                    else:
                        reply = "Mauvais mot de passe."
                        print(reply)
                        conn.send(reply.encode())
                        # essais -= 1
                        # if essais == 0:
                        #    print("Trop de tentatives infructueuses")
                        #    conn.send("auth_stop".encode())
                        #    flag = True
            elif action == "inscrire":
                print(action)
                identifiant = conn.recv(1024).decode()
                mdp = conn.recv(1024).decode()
                print(identifiant, mdp)
                cursor = self.cnx.cursor()
                cursor.execute(f"SELECT * FROM login where Alias like '{identifiant}';")
                results = cursor.fetchall()

                if not results:
                    cursor.execute(f"INSERT INTO login VALUES (0, '{identifiant}', '{mdp}');")
                    self.cnx.commit()
                    cursor.execute(f"SELECT * FROM login where Alias like '{identifiant}';")

                    results = cursor.fetchall()
                    result = results[0]
                    id_client = result[0]
                    cursor.execute(f"INSERT INTO permissions VALUES ({id_client}, 2, 1)")
                    for i in range(3, 7):
                        cursor.execute(f"INSERT INTO permissions VALUES ({id_client}, {i}, 0)")
                        self.cnx.commit()
                    cursor.close()
                    conn.send("inscrip_OK".encode())
                    print("Inscription complète !")
                    listen = threading.Thread(target=self.ecoute, args=[conn, id_client, identifiant])
                    self.listen.append(listen)
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
            salon = conn.recv(1024).decode()
            msg = conn.recv(1024).decode()
            print(salon)
            if salon == "bye" or msg == "bye":
                pass
            else:
                cursor = self.cnx.cursor()
                cursor.execute(f"SELECT * FROM salons where Nom_Salon like '{salon}';")

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
                        except ConnectionError:
                            pass
                        else:
                            pass
                else:
                    perm_ask = "perm_ask"
                    conn.send(perm_ask.encode())
                    perm_denied = "Vous n'avez pas le droit d'envoyer de message dans ce salon."
                    conn.send(perm_denied.encode())

        conn.send("bye".encode())
        print("Client déconnecté")

    def write_bdd(self, msg, id_client, identifiant, id_salon, salon):
        print(f"Writing : {msg}")
        cursor = self.cnx.cursor()
        date = datetime.datetime.now()
        cursor.execute(
            f"INSERT INTO journal VALUES({id_salon},'{salon}',{id_client},'{identifiant}','{msg}','{date}');")
        self.cnx.commit()
        cursor.close()

    def permission(self, salon):
        print(salon)

    def commandes(self):
        reply = ""
        while reply != "kill":
            reply = input("Admin : ")
            print(reply)
        self.stop_serveur = True
        for i in range(len(self.liste_client)):
            try:
                self.liste_client[i].send("bye".encode())
            except ConnectionResetError:
                pass
        self.cnx.close()
        self.server_socket.close()


if __name__ == "__main__":
    serveur = Serveur()
    serveur.main()
