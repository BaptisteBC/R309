import socket
import threading


def ecoute(conn, msg):
    while msg != "bye" and msg != "stop":
        msg = conn.recv(1024).decode()
        print(f"Client : \n {msg}")
    conn.send(msg.encode())


if __name__ == '__main__':
    flag = False
    port = 10000
    msg = ""
    reply = ""

    serveursocket = socket.socket()
    serveursocket.bind(('0.0.0.0', port))
    print(f"Serveur allumé")

    serveursocket.listen(1)
    conn, address = serveursocket.accept()

    while not flag:
        messClients = threading.Thread(target=ecoute, args=[conn, msg])
        messClients.start()

        while reply != "stop":
            reply = str(input("Serveur : "))
            conn.send(reply.encode())
        conn.send(reply.encode())

        messClients.join()
        print(msg)


