-> To use the code in p2pAdvanced/p2p.py:
The most advanced p2p directory
A single Python file with two modes, to use follow these instructions:
Install required Python packages(ubuntu, use brew or arm installs for mac):
pip install fastapi uvicorn sqlalchemy requests pydantic
--or--
pip install -r requirements.txt

1) Discovery server mode (minimal "phonebook"):
   python3 p2pAdvanced/p2p.py --mode discovery --host 0.0.0.0 --port 8000
   - Stores only: username -> ip_address, last_seen
   - Does NOT store messages.

2) P2P node mode (full node):
   python3 p2pAdvanced/p2p.py --mode node --my-port 9001 --username Hilly --ip-addr 10.239.144.58 --discovery-url http://0.0.0.0:8000
            --mode node: Launches the node mode.
            --my-port: The local port on which this node listens for inbound messages.
            --username: Your chosen username.
            --ip-addr: Your public or reachable IP address.
            --discovery-url: The URL of the discovery server.
   - Runs a local FastAPI server on :my-port to receive messages from peers.
   - Has a local SQLite DB for inbound messages (inbox) + "outbox" for messages we tried to send but peer was offline.
   - CLI to register self on the discovery server, list known peers, send messages to them, etc.

The result is a true P2P design:
 - No sensitive data on the central discovery server (just IP + last_seen).
 - Each node is both a server (accepting inbound calls from peers) and a client (sending calls to others).

-> To use the code in ./node/node.py
This is a single file implementation, but simple without backing API or database:
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
