import socket

if __name__ == '__main__':
    flag = False
    port = 10000
    server_socket = socket.socket()
    print("Serveur ouvert")
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)
    conn, address = server_socket.accept()
    while not flag:

        host = socket.gethostname()
        print(f"Client : {host}")
        message = conn.recv(1024).decode()
        print(f"Message reçu : {message}")
        reply = str(input("Réponse du serveur :"))
        conn.send(reply.encode())

        if message == "stop":
            reply = "Au revoir"
            print("Fermeture de la connexion")
            conn.send(reply.encode())
            conn.close()
            server_socket.close()
            flag = True

        elif reply == "bye":
            server_socket.listen(1)
            conn, address = server_socket.accept()


