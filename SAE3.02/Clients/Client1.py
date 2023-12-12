import socket
import threading


def ecoute(reply, stop_sending):
    while reply != "bye" and reply != "stop":
        reply = clientsocket.recv(1024).decode()
        print(f"Serveur : \n {reply}")
    clientsocket.send(reply.encode())
    stop_sending.set()


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 10000
    msg = ""
    reply = ""

    stop_sending = threading.Event()

    clientsocket = socket.socket()
    clientsocket.connect((host, port))
    print("Client connecté")

    messServeur = threading.Thread(target=ecoute, args=[reply, stop_sending])
    messServeur.start()

    while msg != "bye" and msg != "stop" and not stop_sending.is_set():
        msg = str(input("Client : "))
        clientsocket.send(msg.encode())
    clientsocket.send(msg.encode())

    messServeur.join()
    print("Déconnexion")
    clientsocket.close()
