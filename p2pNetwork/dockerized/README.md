# P2P Chat Application

This repository contains a minimal peer‑to‑peer chat application implemented in Python using FastAPI, SQLAlchemy, and SQLite. The project has been dockerized to simplify deployment and testing.

---

## Contents

- `p2p.py` — main application script supporting two modes:
  - **Discovery** mode: a FastAPI server for registering and discovering peer IPs.
  - **Node** mode: a FastAPI server + CLI client for sending and receiving messages.
- `requirements.txt` — Python dependencies
- `Dockerfile` — builds a container image for both discovery and node modes
- `docker-compose.yml` — defines services for discovery and one or more nodes

---

## Prerequisites

- Docker & Docker Compose installed on your machine.
- (Optional) Python 3.10+ if you want to run the script locally without Docker.

---

## Dockerized Setup

### 1. Build the Docker image

From the project root, run:

```bash
docker build -t p2p-chat .
```

This creates the `p2p-chat` image containing Python, dependencies, and `p2p.py`.

### 2. Run via Docker Compose

A `docker-compose.yml` is provided to orchestrate the discovery server and a node:

```bash
docker-compose up -d
```

This will:

- Launch the **discovery** service on port **8000**
- Launch the **node1** service exposing port **9001**

Verify both are running:

```bash
docker-compose ps
```

### 3. Inspect Discovery Service

You can register and list peers using HTTP requests:

- List registered users:
  ```bash
  curl http://localhost:8000/users
  ```

- Register a node:
  ```bash
  curl -X POST http://localhost:8000/register \
    -H "Content-Type: application/json" \
    -d '{"username":"Alice","ip_address":"127.0.0.1"}'
  ```

### 4. Interact with a Node

You can shell into the node container or run the CLI from your host:

#### a) Exec into container:
```bash
docker exec -it <compose_service_name> bash
python p2p.py --mode node \
  --my-port 9001 \
  --username node1 \
  --ip-addr 127.0.0.1 \
  --discovery-url http://discovery:8000
```

#### b) From host (if you have `p2p.py` locally):
```bash
python p2p.py --mode node \
  --my-port 9002 \
  --username hostnode \
  --ip-addr 192.168.1.100 \
  --discovery-url http://localhost:8000
```

Once started you will see an interactive menu:

```
--- P2P Node Menu ---
1) KeepAlive
2) List discovered users
3) Send a message
4) Check inbox
5) Attempt resend of outbox
6) Quit
```

Use these options to communicate with other nodes.

---

## Running Multiple Nodes

To test P2P messaging, run additional node services by copying the `node` block in `docker-compose.yml`, updating:

- Service name (`node2`, `node3`, ...)
- `--username` and `--my-port`

Then restart:

```bash
docker-compose up -d
```

---

## Data Persistence

Both discovery and nodes use SQLite files (`discovery.db`, `p2p_node.db`) stored within the container. To persist these across restarts, mount a host volume in `docker-compose.yml`:

```yaml
services:
  discovery:
    volumes:
      - ./data/discovery.db:/app/discovery.db
  node1:
    volumes:
      - ./data/node1.db:/app/p2p_node.db
```

---

## Cleanup

To stop and remove containers/networks:
```bash
docker-compose down
```

To remove the image:
```bash
docker rmi p2p-chat
```

---

That's it! You now have a multi-container peer discovery and messaging system running in Docker.

