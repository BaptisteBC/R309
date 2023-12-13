import socket
import threading
import mysql.connector


class Serveur:
    def __init__(self, ip='0.0.0.0', port=10000):
        self.conn = None
        self.cnx = None
        self.server_socket = socket.socket()
        self.ip = ip
        self.port = port
        self.max_client = 1
        self.msg = ""
        self.reply = ""
        self.stop_sending = threading.Event()
        self.cnx = mysql.connector.connect(user='root', password='toto', host='127.0.0.1', database='test')

    def admin(self):
        flag = False
        essais = 3
        while not flag:
            identifiant = str(input("Identifiant : "))
            mdp = str(input("Mot de passe : "))

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

    def main(self):
        print("Démarrage du serveur")
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(self.max_client)
        self.conn, address = self.server_socket.accept()

        listen = threading.Thread(target=self.ecoute)
        listen.start()

        while self.reply != "stop" and self.reply != "bye" and not self.stop_sending.is_set():
            self.reply = str(input("Serveur : "))
            self.conn.send(self.reply.encode())

        listen.join()

    def ecoute(self):
        print(self.reply)
        while self.msg != "bye" and self.msg != "stop":
            self.msg = self.conn.recv(1024).decode()
            print(f"Client : \n {self.msg}")
            self.write_bdd()
        self.reply = "bye"
        self.conn.send(self.reply.encode())
        print("Client déconnecté")
        self.stop_sending.set()

    def write_bdd(self):
        print(f"Writing : {self.msg}")
        cursor = self.cnx.cursor()
        cursor.execute(f"INSERT INTO messages VALUES(0,'{self.msg}');")
        self.cnx.commit()
        cursor.close()

    def id_client(self):
        pass


if __name__ == "__main__":
    serveur = Serveur()
    serveur.admin()
