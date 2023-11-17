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
    msg = ""
    reply = ""

    server_socket = socket.socket()
    print("Serveur ouvert")
    server_socket.bind(('0.0.0.0', port))

    server_socket.listen(1)
    conn, address = server_socket.accept()

    while msg != "bye" and msg != "stop" and reply != "bye" and reply != "stop":
        t1 = threading.Thread(target=receive, args=[conn])
        t1.start()

        reply = str(input("Serveur :"))
        conn.send(reply.encode())

