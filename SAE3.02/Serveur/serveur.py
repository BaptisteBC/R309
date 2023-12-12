import socket
import threading


class Serveur():
    def __init__(self):
        self.reply = ""
        self.serveursocket = socket.socket()
        self.nb_clients = 2

    def main(self):
        flag = False
        port = 10000
        stop_sending = threading.Event()

        self.serveursocket.bind(('0.0.0.0', port))
        print(f"Serveur allumé")

        self.serveursocket.listen(self.nb_clients)

        while not flag:

            conn, address = self.serveursocket.accept()
            print(conn, address)

            messClients = threading.Thread(target=self.ecoute, args=[conn, stop_sending])
            messClients.start()

            while self.reply != "stop" and not stop_sending.is_set():
                reply = str(input("Serveur : "))
                conn.send(reply.encode())
            stop_sending.set()

            messClients.join()

    def ecoute(self, conn, stop_sending):
        msg = ""
        while msg != "bye" and msg != "stop" and not stop_sending.is_set():
            msg = conn.recv(1024).decode()
            print(f"Client : \n {msg}")
        reply = "bye"
        conn.send(reply.encode())
        stop_sending.set()


if __name__ == '__main__':
    Serveur.main(Serveur)
