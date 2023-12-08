import socket
import threading


def ecoute(reply):
    while reply != "bye" and reply != "stop":
        reply = clientsocket.recv(1024).decode()
        print(f"Serveur : \n {reply}")


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 10000
    msg = ""
    reply = ""

    clientsocket = socket.socket()
    clientsocket.connect((host, port))
    print("Client connecté")

    messServeur = threading.Thread(target=ecoute, args=[reply])
    messServeur.start()

    while msg != "bye" and msg != "stop":
        msg = str(input("Client : "))
        clientsocket.send(msg.encode())

    messServeur.join()
