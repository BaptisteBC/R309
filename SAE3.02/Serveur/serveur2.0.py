import socket
import threading
import mysql.connector


class Serveur:
    def __init__(self, ip='0.0.0.0', port=10000):
        self.cnx = None
        self.server_socket = socket.socket()
        self.ip = ip
        self.port = port
        self.max_client = 2
        self.msg = ""
        self.reply = ""
        self.stop_sending = threading.Event()
        self.cnx = mysql.connector.connect(user='root', password='toto', host='127.0.0.1', database='test')
        self.liste_client = []

    def admin(self):
        flag = False
        essais = 3
        while not flag:
            # identifiant = str(input("Identifiant : "))
            # mdp = str(input("Mot de passe : "))
            identifiant = "toto"
            mdp = "toto"

            cursor = self.cnx.cursor()
            cursor.execute(f"SELECT * FROM login where nom like '{identifiant}';")
            results = cursor.fetchall()
            if not results:
                print("Identifiant invalide")
                essais -= 1
                if essais == 0:
                    print("Trop de tentatives infructueuses")
                    flag = True
            else:
                result = results[0]
                # print(result)
                cursor.close()

                if result[2] == mdp:
                    print(f"Connexion réussie \n Bienvenue Administrateur !")
                    self.main()

                    flag = True
                else:
                    print("Mauvais mot de passe")
                    essais -= 1
                    if essais == 0:
                        print("Trop de tentatives infructueuses")
                        flag = True

    def accept(self, conn):
        listen = threading.Thread(target=self.ecoute, args=[conn])
        listen.start()

        while self.reply != "stop" and self.reply != "bye" and not self.stop_sending.is_set():
            self.reply = str(input("Serveur : "))
            conn.send(self.reply.encode())

        listen.join()

    def main(self):
        print("Démarrage du serveur")
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(self.max_client)

        for i in range(self.max_client):

            conn, address = self.server_socket.accept()
            self.liste_client.append(conn)
            client_accept = threading.Thread(target=self.accept, args=[conn])
            client_accept.start()

    def ecoute(self, conn):
        print(self.reply)
        msg = ""
        while msg != "bye" and msg != "stop" and not self.stop_sending.is_set():
            msg = conn.recv(1024).decode()
            print(f"Client : \n {msg}")
            self.write_bdd(msg)
            for i in range(len(self.liste_client)):
                if self.liste_client[i] == conn and msg == "bye":
                    pass
                else:
                    self.liste_client[i].send(msg.encode())

        self.reply = "bye"
        conn.send(self.reply.encode())
        print("Client déconnecté")
        self.stop_sending.set()

    def write_bdd(self, msg):
        print(f"Writing : {msg}")
        cursor = self.cnx.cursor()
        cursor.execute(f"INSERT INTO messages VALUES(0,'{msg}');")
        self.cnx.commit()
        cursor.close()

    def id_client(self):
        pass


if __name__ == "__main__":
    serveur = Serveur()
    serveur.admin()
