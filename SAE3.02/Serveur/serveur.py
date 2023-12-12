import socket
import threading


def ecoute(conn, stop_sending):
    msg = ""
    while msg != "bye" and msg != "stop" and not stop_sending.is_set():
        msg = conn.recv(1024).decode()
        print(f"Client : \n {msg}")
    reply = "bye"
    conn.send(reply.encode())
    stop_sending.set()


def accept():



if __name__ == '__main__':
    flag = False
    port = 10000
    reply = ""
    stop_sending = threading.Event()
    serveursocket = socket.socket()
    nb_clients = 2

    serveursocket.bind(('0.0.0.0', port))
    print(f"Serveur allumé")

    serveursocket.listen(nb_clients)

    while not flag:
        for i in range(nb_clients):
            conn, address = serveursocket.accept()
            print(conn, address)

        accept = threading.Thread(target=accept)
        accept.start()

        messClients = threading.Thread(target=ecoute, args=[conn, stop_sending])
        messClients.start()

        while reply != "stop" and not stop_sending.is_set():
            reply = str(input("Serveur : "))
            conn.send(reply.encode())
        stop_sending.set()

        messClients.join()
        accept.join()
