import socket
import threading


def receive(conn):
    msg = ""
    while msg != "bye" and msg != "stop":
        msg = conn.recv(1024).decode()
        host = socket.gethostname()
        print(f"Client {host} : {msg}")


if __name__ == '__main__':
    flag = False
    port = 10000

    server_socket = socket.socket()
    print("Serveur ouvert")
    server_socket.bind(('0.0.0.0', port))

    server_socket.listen(1)
    conn, address = server_socket.accept()

    while not flag:
        reply = ""

        ecoute = threading.Thread(target=receive, args=[conn])
        ecoute.start()

        while reply != "bye" and reply != "stop":
            reply = str(input("Serveur :"))
            conn.send(reply.encode())

        ecoute.join()

        if reply == "bye":
            print("En attente d'un nouveau client")
            server_socket.listen(1)
            conn, address = server_socket.accept()
