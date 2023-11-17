import socket

if __name__ == '__main__':
    flag = False
    host = "127.0.0.1"
    port = 10000

    client_socket = socket.socket()
    client_socket.connect((host, port))
    print("Client connecté")

    while not flag:
        message = str(input("Votre message : "))
        client_socket.send(message.encode())

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
                message = str("bye")
                client_socket.send(message.encode())
                client_socket.close()
                flag = True
            if reply == "stop":
                print("Fin de la connexion")
                client_socket.close()
                flag = True
