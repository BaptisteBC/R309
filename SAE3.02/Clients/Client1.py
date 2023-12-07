import socket
import threading


def reception():
    reply = ""
    while reply != "bye" and reply != "stop":
        reply = client_socket.recv(1024).decode()
        print(f"Client : {reply}")


if __name__ == '__main__':
    port = 10000

    client_socket = socket.socket()
    client_socket.connect(("127.0.0.1", port))
    print("Client connecté")

    flag = False
    while not flag:

        ecoute = threading.Thread(target=reception)
        ecoute .start()

        while msg != "stop" and msg != "bye":

            msg = str(input("Votre message : "))
            client_socket.send(msg.encode())

        if message == "stop":
            print("Fin de la connexion")
            client_socket.close()
            flag = True
        elif message == "bye":
            print("Déconnexion")
            client_socket.close()
            flag = True
        else:
            reply = client_socket.recv(1024).decode()
            print(f"Serveur : \n {reply}")

            if reply == "bye":
                print("Déconnexion")
                client_socket.close()
                flag = True
            if reply == "stop":
                print("Fin de la connexion")
                client_socket.close()
                flag = True
