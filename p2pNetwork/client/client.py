import socket
import threading

from config import SERVER_HOST, SERVER_PORT

def receive_messages(client_socket):
    """Continuously receive messages from the server."""
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                print("Connection closed by server.")
                client_socket.close()
                break
            print(message.decode())
        except Exception as e:
            print("Error receiving:", e)
            client_socket.close()
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")

    # Start a thread to receive messages.
    thread = threading.Thread(target=receive_messages, args=(client_socket,))
    thread.daemon = True
    thread.start()

    # Send messages in the main thread.
    while True:
        message = input("")
        if message.lower() == "quit":
            client_socket.close()
            break
        client_socket.send(message.encode())

if __name__ == "__main__":
    main()
