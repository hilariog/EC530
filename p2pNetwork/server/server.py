import socket
import threading
from config import HOST, PORT

# Global list to track connected client sockets.
clients = []

def broadcast(message, current_client):
    """Send the message to all clients except the sender."""
    for client in clients:
        if client != current_client:
            try:
                client.send(message)
            except Exception as e:
                print("Error broadcasting:", e)

def handle_client(client_socket, address):
    """Handle communication with a connected client."""
    print(f"New connection from {address}")
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                print(f"Connection closed by {address}")
                clients.remove(client_socket)
                client_socket.close()
                break
            print(f"Received from {address}: {message.decode()}")
            broadcast(message, client_socket)
        except Exception as e:
            print(f"Error with client {address}: {e}")
            clients.remove(client_socket)
            client_socket.close()
            break

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == "__main__":
    start_server()
