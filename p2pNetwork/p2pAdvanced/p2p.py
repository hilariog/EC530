#!/usr/bin/env python3

import argparse
import sys
import time
import datetime
import threading
from typing import Optional, List
import uvicorn
import requests
from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
from sqlalchemy import (create_engine, Column, Integer, String, DateTime,
                        Boolean, Text)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

# ---------------------------------------------------------------------------------
# GLOBALS / CONFIG
# ---------------------------------------------------------------------------------
Base = declarative_base()

# We'll use separate DB files for discovery vs node.
DISCOVERY_DB_URL = "sqlite:///discovery.db"
NODE_DB_URL = "sqlite:///p2p_node.db"

# ==============================
# 1) DISCOVERY SERVER CLASSES
# ==============================
class DiscoveryUser(Base):
    """
    Minimal table for the discovery server:
    (username, ip_address, last_seen).
    No messages are stored here!
    """
    __tablename__ = "discovery_users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True)
    ip_address = Column(String(64))
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)


# ==============================
# 2) P2P NODE DB CLASSES
# ==============================
class OutboxMessage(Base):
    """
    For messages we tried to send but haven't confirmed delivered to the peer.
    We'll store them and attempt to re-send later.
    """
    __tablename__ = "outbox"
    id = Column(Integer, primary_key=True, index=True)
    to_user = Column(String(64), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class InboxMessage(Base):
    """
    For messages we've received from peers. If we were offline, they couldn't deliver,
    so they'd hold them in *their* outbox. Once we come online, they can deliver to us.
    """
    __tablename__ = "inbox"
    id = Column(Integer, primary_key=True, index=True)
    from_user = Column(String(64), nullable=False)
    content = Column(Text, nullable=False)
    received_at = Column(DateTime, default=datetime.datetime.utcnow)

# ---------------------------------------------------------------------------------
# DISCOVERY SERVER MODE
# ---------------------------------------------------------------------------------
discovery_app = FastAPI(title="Minimal Discovery Server", docs_url=None, redoc_url=None)

class UserRegister(BaseModel):
    username: str
    ip_address: str

class KeepAlive(BaseModel):
    username: str

def init_discovery_db():
    engine = create_engine(DISCOVERY_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()

@discovery_app.post("/register")
def register_user(payload: UserRegister):
    """Register or update a user with IP in the discovery server."""
    session = init_discovery_db()
    user = session.query(DiscoveryUser).filter_by(username=payload.username).first()
    if user:
        user.ip_address = payload.ip_address
        user.last_seen = datetime.datetime.utcnow()
    else:
        user = DiscoveryUser(
            username=payload.username,
            ip_address=payload.ip_address,
            last_seen=datetime.datetime.utcnow()
        )
        session.add(user)
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "ok", "message": f"User {payload.username} registered/updated."}

@discovery_app.post("/keepalive")
def keepalive(payload: KeepAlive):
    """Update last_seen for a user to indicate they're still alive."""
    session = init_discovery_db()
    user = session.query(DiscoveryUser).filter_by(username=payload.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.last_seen = datetime.datetime.utcnow()
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "ok", "message": "Keepalive updated"}

@discovery_app.get("/users")
def list_users():
    """
    Return all known users with IP addresses. (Could add logic to filter out
    very stale last_seen if we want.)
    """
    session = init_discovery_db()
    all_users = session.query(DiscoveryUser).all()
    results = []
    for u in all_users:
        results.append({
            "username": u.username,
            "ip_address": u.ip_address,
            "last_seen": u.last_seen.isoformat()
        })
    return results

# We'll run this with uvicorn if --mode=discovery

# ---------------------------------------------------------------------------------
# P2P NODE MODE
# ---------------------------------------------------------------------------------
node_app = FastAPI(title="P2P Node", docs_url=None, redoc_url=None)

def init_node_db():
    engine = create_engine(NODE_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()

class DeliverMessagePayload(BaseModel):
    from_user: str
    content: str

@node_app.post("/deliver_message")
def deliver_message(payload: DeliverMessagePayload):
    """
    Called by a remote peer who wants to send us a message directly.
    We store it in our local inbox.
    """
    session = init_node_db()
    msg = InboxMessage(
        from_user=payload.from_user,
        content=payload.content
    )
    session.add(msg)
    try:
        session.commit()
        session.refresh(msg)
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "ok", "inbox_id": msg.id}

# We'll run this node_app with uvicorn if --mode=node

# ---------------------------------------------------------------------------------
# NODE HELPER FUNCTIONS
# ---------------------------------------------------------------------------------

def discovery_register(discovery_url: str, username: str, ip_addr: str):
    """
    Register or update user on the discovery server.
    """
    payload = {"username": username, "ip_address": ip_addr}
    r = requests.post(f"{discovery_url}/register", json=payload)
    r.raise_for_status()
    return r.json()

def discovery_keepalive(discovery_url: str, username: str):
    payload = {"username": username}
    r = requests.post(f"{discovery_url}/keepalive", json=payload)
    r.raise_for_status()
    return r.json()

def discovery_list_users(discovery_url: str):
    r = requests.get(f"{discovery_url}/users")
    r.raise_for_status()
    return r.json()  # list of {username, ip_address, last_seen}


def node_deliver_message(peer_ip: str, peer_port: int, from_user: str, content: str):
    """
    Send an HTTP POST to the peer's /deliver_message endpoint.
    If it fails (peer offline), raise an exception so we can store in outbox.
    """
    url = f"http://{peer_ip}:{peer_port}/deliver_message"
    payload = {"from_user": from_user, "content": content}
    r = requests.post(url, json=payload, timeout=5)  # short timeout for example
    r.raise_for_status()
    return r.json()


def store_outbox_message(to_user: str, content: str):
    session = init_node_db()
    msg = OutboxMessage(to_user=to_user, content=content)
    session.add(msg)
    try:
        session.commit()
        session.refresh(msg)
    except SQLAlchemyError as e:
        session.rollback()
        print(f"[ERROR] Could not store outbox message: {e}")


def attempt_resend_outbox(username: str, discovery_url: str, listen_port: int):
    """
    Attempt to send all outbox messages. For each message, see if we can find
    the recipient's IP from the discovery server. If so, deliver directly.
    If success, remove from outbox.
    """
    session = init_node_db()
    outbox = session.query(OutboxMessage).all()

    # Get list of all users from discovery
    try:
        users = discovery_list_users(discovery_url)
    except Exception as e:
        print(f"[WARN] Could not fetch user list: {e}")
        return

    # Create a dict: username -> ip
    user_ip_map = {}
    for u in users:
        uname = u["username"]
        ip = u["ip_address"]
        user_ip_map[uname] = ip

    for msg in outbox:
        to_user = msg.to_user
        content = msg.content
        if to_user not in user_ip_map or not user_ip_map[to_user]:
            print(f"[INFO] No known IP for user {to_user}, skipping message {msg.id}.")
            continue

        peer_ip = user_ip_map[to_user]
        if not peer_ip:
            print(f"[INFO] User {to_user} has no IP, skipping.")
            continue

        # Assume the peer node is listening on the same port we do, or it might store its own port somewhere else
        # For demonstration, let's guess they're on the same port  ( or you could store user->port in discovery too )
        try:
            node_deliver_message(peer_ip, listen_port, username, content)
            print(f"[OUTBOX] Successfully delivered msg {msg.id} to {to_user}. Removing from outbox.")
            session.delete(msg)
            session.commit()
        except Exception as e:
            print(f"[OUTBOX] Could not deliver msg {msg.id} to {to_user} at {peer_ip}:{listen_port}: {e}")

    session.close()


def read_inbox():
    """
    Read all messages in the local inbox.
    """
    session = init_node_db()
    messages = session.query(InboxMessage).order_by(InboxMessage.id).all()
    if not messages:
        print("[INBOX] No messages.")
        return
    print("[INBOX] Messages:")
    for m in messages:
        print(f"  From: {m.from_user}  Content: {m.content}  Received: {m.received_at}")
    # For demonstration, we won't delete them automatically, but you could.
    session.close()

# ---------------------------------------------------------------------------------
# MAIN / ARGPARSE
# ---------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="P2P Communication with minimal discovery server."
    )
    parser.add_argument("--mode", choices=["discovery", "node"], default="discovery",
                        help="Which mode to run: 'discovery' or 'node'.")
    parser.add_argument("--host", default="0.0.0.0",
                        help="Host IP to bind if in 'discovery' mode.")
    parser.add_argument("--port", type=int, default=8000,
                        help="Port to bind if in 'discovery' mode.")
    parser.add_argument("--my-port", type=int, default=9001,
                        help="Port to bind if in 'node' mode.")
    parser.add_argument("--username", default="Alice",
                        help="Username for node mode.")
    parser.add_argument("--ip-addr", default="127.0.0.1",
                        help="Public IP or reachable IP of this node (for node mode).")
    parser.add_argument("--discovery-url", default="http://127.0.0.1:8000",
                        help="URL of the discovery server (for node mode).")
    args = parser.parse_args()

    if args.mode == "discovery":
        # Just run the minimal discovery server
        print(f"[DISCOVERY] Running on {args.host}:{args.port}")
        # We'll create the DB if not present
        engine = create_engine(DISCOVERY_DB_URL, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        uvicorn.run(discovery_app, host=args.host, port=args.port, log_level="info")

    else:
        # NODE MODE
        # 1) Start local FastAPI server for receiving messages
        #    We'll do it in a thread so we can also do CLI in the main thread.
        def start_node_server():
            uvicorn.run(node_app, host="0.0.0.0", port=args.my_port, log_level="info")

        server_thread = threading.Thread(target=start_node_server, daemon=True)
        server_thread.start()
        time.sleep(1)
        print(f"[NODE] Started local server thread on port {args.my_port}.")

        # 2) Register with discovery server
        while True:
            try:
                resp = discovery_register(args.discovery_url, args.username, args.ip_addr)
                print(f"[NODE] Register response: {resp}")
                break
            except Exception as e:
                print(f"[ERROR] Could not register with discovery: {e}")
                retry = input("Retry? (y/n): ").lower()
                if retry != 'y':
                    sys.exit(1)

        # 3) Main CLI loop
        while True:
            print("\n--- P2P Node Menu ---")
            print("1) KeepAlive")
            print("2) List discovered users")
            print("3) Send a message")
            print("4) Check inbox")
            print("5) Attempt resend of outbox")
            print("6) Quit")
            choice = input("Enter choice: ").strip()
            if choice == '1':
                # KeepAlive
                try:
                    resp = discovery_keepalive(args.discovery_url, args.username)
                    print("[KEEPALIVE]", resp)
                except Exception as e:
                    print("[ERROR]", e)
            elif choice == '2':
                # List users
                try:
                    users = discovery_list_users(args.discovery_url)
                    print("[USERS]")
                    for u in users:
                        last_seen_ago = datetime.datetime.utcnow() - datetime.datetime.fromisoformat(u["last_seen"])
                        print(f"  {u['username']}: IP={u['ip_address']}  last_seen={last_seen_ago.total_seconds():.1f}s ago")
                except Exception as e:
                    print("[ERROR]", e)
            elif choice == '3':
                # Send a message
                to_user = input("Send to which user?: ").strip()
                content = input("Message content: ")
                # We need that user's IP from the discovery server
                try:
                    users = discovery_list_users(args.discovery_url)
                    peer_ip = None
                    for u in users:
                        if u["username"] == to_user:
                            peer_ip = u["ip_address"]
                            break
                    if not peer_ip:
                        print("[INFO] That user not found or no IP in discovery. Storing in outbox.")
                        store_outbox_message(to_user, content)
                        continue

                    # Attempt direct deliver
                    # We assume the node listens on the same port we do. 
                    # If you want each user to store a custom port, you'd add it to the discovery server.
                    node_deliver_message(peer_ip, args.my_port, args.username, content)
                    print("[SEND] Delivered directly!")
                except Exception as e:
                    print(f"[SEND] Could not deliver: {e}. Storing in outbox.")
                    store_outbox_message(to_user, content)
            elif choice == '4':
                # Read our local inbox
                read_inbox()
            elif choice == '5':
                # Attempt resend of outbox
                attempt_resend_outbox(args.username, args.discovery_url, args.my_port)
            elif choice == '6':
                print("[NODE] Exiting.")
                sys.exit(0)
            else:
                print("[ERROR] Invalid choice. Try again.")


if __name__ == "__main__":
    main()
