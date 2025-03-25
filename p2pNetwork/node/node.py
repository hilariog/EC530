#!/usr/bin/env python3
import socket
import threading
import sys
import argparse

# Default configuration values.
DEFAULT_PORT = 12345

def handle_client(conn, addr):
    """Thread function to handle an incoming connection."""
    print(f"[SERVER] Connection from {addr} established.")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                # Connection closed by client.
                break
            print(f"[RECEIVED from {addr}] {data.decode()}")
    except Exception as e:
        print(f"[SERVER] Error with connection {addr}: {e}")
    finally:
        print(f"[SERVER] Connection from {addr} closed.")
        conn.close()

def server_thread(listen_port):
    """Server thread that listens for incoming connections."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Listen on all interfaces.
    s.bind(('0.0.0.0', listen_port))
    s.listen(5)
    print(f"[SERVER] Listening for connections on port {listen_port}...")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def client_receive(s, peer_info):
    """Thread to continuously receive messages from a connected peer."""
    try:
        while True:
            data = s.recv(1024)
            if not data:
                break
            print(f"[PEER {peer_info}] {data.decode()}")
    except Exception as e:
        print(f"[CLIENT] Error receiving from {peer_info}: {e}")
    finally:
        print(f"[CLIENT] Connection to {peer_info} closed.")
        s.close()

def client_connect(target_ip, target_port):
    """Function to connect as a client to another node and send messages."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((target_ip, target_port))
        print(f"[CLIENT] Connected to {target_ip}:{target_port}")
        # Start a thread to receive messages from the peer.
        threading.Thread(target=client_receive, args=(s, f"{target_ip}:{target_port}"), daemon=True).start()
        # Main loop for sending messages.
        while True:
            msg = input("Enter message (or 'quit' to disconnect): ")
            if msg.lower() == 'quit':
                break
            s.send(msg.encode())
    except Exception as e:
        print(f"[CLIENT] Error connecting to {target_ip}:{target_port}: {e}")
    finally:
        s.close()

def main():
    parser = argparse.ArgumentParser(description="P2P Node for Pokemon Game")
    parser.add_argument('--port', type=int, default=DEFAULT_PORT,
                        help="Port on which this node will listen for incoming connections")
    args = parser.parse_args()

    # Start the server thread using the specified listening port.
    threading.Thread(target=server_thread, args=(args.port,), daemon=True).start()
    print(f"[INFO] Server thread started. Listening on port {args.port}.")

    # Main loop to interact as a client.
    while True:
        print("\nOptions:")
        print("1. Connect to a peer and send messages")
        print("2. Quit")
        choice = input("Enter choice: ")
        if choice == '1':
            target_ip = input("Enter target IP address: ")
            target_port_str = input("Enter target port: ")
            try:
                target_port = int(target_port_str)
            except ValueError:
                print("[CLIENT] Invalid port number. Using default port.")
                target_port = DEFAULT_PORT
            client_connect(target_ip, target_port)
        elif choice == '2':
            print("[INFO] Exiting...")
            sys.exit(0)
        else:
            print("[INFO] Invalid option. Please try again.")

if __name__ == '__main__':
    main()
