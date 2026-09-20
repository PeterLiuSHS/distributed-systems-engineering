import socket

def main():
    host = 'localhost'
    port = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Server is listening on port {port}")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"New client connected from {client_address}")

            with client_socket:
                data = client_socket.recv(1024).decode('utf-8')
                print(f"Received {data}")

                response = data.upper()

                client_socket.send(response.encode('utf-8'))
                print(f"Sent {response}")

            print("Client disconnected")

if __name__ == '__main__':
    main()