import os
import socket

def main():
    host = os.getenv("APP", "127.0.0.1")
    port = int(os.getenv("PORT", 8080))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print(f"Connected to {host}:{port}")

        message = input("Please enter a message: ")
        print(f"Sent: {message}")

        client_socket.send(message.encode('utf-8'))

        response = client_socket.recv(1024).decode('utf-8')
        print(f"Received: {response}")

if __name__ == '__main__':
    main()