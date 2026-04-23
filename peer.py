import socket
import threading
import os

HOST = "127.0.0.1"
PORT = 5000

# ----------- SERVIDOR (recibe conexiones) ----------
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[LISTENING] {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn,)).start()


def handle_client(conn):
    while True:
        data = conn.recv(1024)

        if not data:
            break

        message = data.decode()

        if message.startswith("MSG:"):
            print(f"[NOTIFICACIÓN] {message[4:]}")

        elif message.startswith("FILE:"):
            filename = message.split(":")[1]
            receive_file(conn, filename)

    conn.close()


# ----------- RECIBIR ARCHIVO ----------
def receive_file(conn, filename):
    with open(f"archivos/{filename}", "wb") as f:
        while True:
            data = conn.recv(1024)
            if data == b"EOF":
                break
            f.write(data)

    print(f"[ARCHIVO RECIBIDO] {filename}")


# ----------- CLIENTE (envía datos) ----------
def send_message(ip, port, msg):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))

    client.send(f"MSG:{msg}".encode())
    client.close()


def send_file(ip, port, filepath):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))

    filename = os.path.basename(filepath)
    client.send(f"FILE:{filename}".encode())

    with open(filepath, "rb") as f:
        while True:
            bytes_read = f.read(1024)
            if not bytes_read:
                break
            client.send(bytes_read)

    client.send(b"EOF")
    client.close()

    print("[ARCHIVO ENVIADO]")


# ----------- MAIN ----------
if __name__ == "__main__":
    threading.Thread(target=start_server).start()

    while True:
        print("\n1. Enviar mensaje")
        print("2. Enviar archivo")

        option = input("> ")

        ip = input("IP destino: ")
        port = int(input("Puerto: "))

        if option == "1":
            msg = input("Mensaje: ")
            send_message(ip, port, msg)

        elif option == "2":
            path = input("Ruta del archivo: ")
            send_file(ip, port, path)