import threading
import socket


def reception(conn):
    msg = ""
    while msg != "bye" and msg != "stop":
        msg = conn.recv(1024).decode()
        print(f"Client : {msg}")
    conn.send(msg.encode())
    return msg


def arretServeur(conn, server_socket):
    conn.close()
    server_socket.close()


if __name__ == "__main__":
    port = 10000

    server_socket = socket.socket()
    print("Serveur ouvert")
    server_socket.bind(('0.0.0.0', port))

    server_socket.listen(1)
    conn, address = server_socket.accept()

    flag = False
    while not flag:
        ecoute = threading.Thread(target=reception, args=[conn])
        ecoute.start()

        reply = ""
        while reply != "bye" and reply != "stop":
            reply = str(input("Serveur :"))
            conn.send(reply.encode())
        conn.send(reply.encode())

        ecoute.join()

        if reply == "bye":
            conn.close()
            print("En attente d'un nouveau client")
            server_socket.listen(1)
            conn, address = server_socket.accept()

        if reply == "stop":
            reply = "Au revoir"
            print("Fermeture de la connexion")
            conn.send(reply.encode())
            arretServeur(conn, server_socket)
            flag = True
