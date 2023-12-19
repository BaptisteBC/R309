import socket
import threading
import mysql.connector


class Serveur:
    def __init__(self, ip='0.0.0.0', port=10000, max_client=5, sql_user='root', sql_mdp='toto', sql_host='127.0.0.1'):
        self.client_accept = None
        self.server_socket = socket.socket()
        self.ip = ip
        self.port = port
        self.max_client = max_client
        self.msg = ""
        self.reply = ""
        self.stop_sending = threading.Event()
        self.cnx = mysql.connector.connect(user=sql_user, password=sql_mdp, host=sql_host, database='test')
        self.liste_client = []
        self.stop_serveur = False

    def accept(self, conn):
        reply = "Client connecté !"
        print(reply, conn)
        conn.send(reply.encode())

        self.auth(conn)

        listen = threading.Thread(target=self.ecoute, args=[conn])
        listen.start()

        listen.join()

    def auth(self, conn):

        flag = False
        essais = 3
        while not flag:
            action = conn.recv(1024).decode()
            if action == "auth":
                print(action)

                identifiant = conn.recv(1024).decode()
                print(identifiant)
                mdp = conn.recv(1024).decode()
                print(mdp)
                cursor = self.cnx.cursor()
                cursor.execute(f"SELECT * FROM login where nom like '{identifiant}';")
                results = cursor.fetchall()
                cursor.close()
                if not results:
                    reply = "Identifiant introuvable, réessayez."
                    print(reply)
                    conn.send(reply.encode())
                    essais -= 1
                    if essais == 0:
                        reply = "auth_stop"
                        print(reply)

                        conn.send(reply.encode())
                        flag = True
                else:
                    result = results[0]
                    print(result)

                    if result[2] == mdp:
                        reply = "auth_OK"
                        conn.send(reply.encode())
                        print(reply)
                        conf_auth = "auth_OK"
                        conn.send(conf_auth.encode())

                        flag = True
                    else:
                        reply = "Mauvais mot de passe."
                        print(reply)
                        conn.send(reply.encode())
                        essais -= 1
                        if essais == 0:
                            print("Trop de tentatives infructueuses")
                            conn.send("auth_stop".encode())
                            flag = True
            elif action == "inscrire":
                print(action)
                identifiant = conn.recv(1024).decode()
                mdp = conn.recv(1024).decode()
                print(identifiant, mdp)
                cursor = self.cnx.cursor()
                cursor.execute(f"SELECT * FROM login where nom like '{identifiant}';")
                results = cursor.fetchall()
                if not results:
                    cursor.execute(f"INSERT INTO login VALUES (0, '{identifiant}', '{mdp}');")
                    self.cnx.commit()
                    cursor.close()
                    conn.send("inscrip_OK".encode())
                    print("Inscription complète !")
                    flag = True
                else:
                    cursor.close()
                    reply = "Try again"
                    conn.send(reply.encode())

    def main(self):
        print("Démarrage du serveur")
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(self.max_client)

        while not self.stop_serveur:
            conn, address = self.server_socket.accept()
            self.liste_client.append(conn)
            self.client_accept = threading.Thread(target=self.accept, args=[conn])
            self.client_accept.start()

        self.client_accept.join()

    def ecoute(self, conn):
        msg = ""
        while msg != "bye" and msg != "stop" and not self.stop_sending.is_set() and not self.stop_serveur:
            msg = conn.recv(1024).decode()
            print(f"Client : {msg}")
            self.write_bdd(msg)
            for i in range(len(self.liste_client)):
                if self.liste_client[i] == conn or msg == "bye":
                    pass
                else:
                    self.liste_client[i].send(msg.encode())

        print("Client déconnecté")
        conn.send("bye".encode())
    def write_bdd(self, msg):
        print(f"Writing : {msg}")
        cursor = self.cnx.cursor()
        cursor.execute(f"INSERT INTO messages VALUES(0,'{msg}');")
        self.cnx.commit()
        cursor.close()


if __name__ == "__main__":
    serveur = Serveur()
    serveur.main()
