import socket
import threading


def ecoute(stop_sending):
    reply = ""
    while reply != "bye" and reply != "stop" and not stop_sending.is_set():
        reply = clientsocket.recv(1024).decode()
        print(f"Serveur : \n {reply}")
    msg = "bye"
    clientsocket.send(msg.encode())
    stop_sending.set()


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 10000
    msg = ""

    stop_sending = threading.Event()

    clientsocket = socket.socket()
    clientsocket.connect((host, port))
    print("Client connecté")

    messServeur = threading.Thread(target=ecoute, args=[stop_sending])
    messServeur.start()

    while msg != "bye" and msg != "stop" and not stop_sending.is_set():
        print(1)
        msg = str(input("Client : "))
        clientsocket.send(msg.encode())
    stop_sending.set()

    messServeur.join()
    print("Déconnexion")
    clientsocket.close()
