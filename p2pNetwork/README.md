Use the code in ./node/node.py
This is the single file implementation of p2p messaging system
To use this as a client, run the node.py file, passing your IP address as an argument. It will prompt you choose a port:

SHELL: python3 node/node.py --port <my_listening_port> //Use the port you are listening from

When you connect it will prompt you:

hilariogonzalez@crc-dot1x-nat-10-239-144-58 p2pNetwork % python3 node/node.py --port 12345

[INFO] Server thread started. Listening on port 12345.

Options:
1. Connect to a peer and send messages
2. Quit

Enter choice: [SERVER] Listening for connections on port 12345...

1

Enter target IP address: 0.0.0.0

Enter target port: 12346

[CLIENT] Connected to 0.0.0.0:12346

Enter message (or 'quit' to disconnect): [SERVER] Connection from ('127.0.0.1', 53445) established.

Hi

Enter message (or 'quit' to disconnect): [RECEIVED from ('127.0.0.1', 53445)] Hi

Hey
