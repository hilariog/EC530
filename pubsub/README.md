# A pub sub implementation of smart home api using redis

This project is a FastAPI-based smart home backend using Redis for Pub/Sub messaging. It builds on a simple in-memory home API, adding live event streams so clients can subscribe to device/user/room updates in real time.

## Prerequisites

- **Python 3.9+**
- **Redis** (local or remote)
- (Recommended) **virtualenv** or **venv** for isolation

## 1. Clone & Create Virtual Environment

```bash
git clone <repo-url> smart-home-pubsub
cd smart-home-pubsub
python3 -m venv venv
source venv/bin/activate
```

## 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
# requirements.txt includes:
# fastapi
# uvicorn[standard]
# redis
# pydantic
```

## 3. Start Redis

### macOS (Homebrew)
```bash
brew update
brew install redis
brew services start redis
```  
### Docker
```bash
docker run -d --name redis -p 6379:6379 redis:latest
```

Verify Redis is running:
```bash
redis-cli ping   # should reply: PONG
```

## 4. Configuration

By default, the app connects to Redis at `redis://localhost:6379/0`. To change this, set the `REDIS_URL` environment variable before launching:

```bash
export REDIS_URL=redis://myuser:mypassword@redis-host:6379/1
```

## 5. Run the API

Use the virtualenv’s interpreter to ensure the correct environment:

```bash
python -m uvicorn main:app --reload --port 8000
```

- **`--reload`** watches for code changes
- **`--port 8000`** serves on port 8000

## 6. Endpoints & Pub/Sub

### REST Endpoints
All CRUD actions auto-publish events to Redis channels named after the model (e.g. `users`, `rooms`, `devices`, `houses`).

- **Users**:  
  - `POST /users` → create user  
  - `GET /users` → list  
  - `DELETE /users/{id}` → delete

- **Houses**:  
  - `POST /houses`  
  - `GET /houses`  
  - `DELETE /houses/{id}`

- **Rooms**:  
  - `POST /rooms`  
  - `GET /rooms`  
  - `PUT /rooms/{id}/assign_user?user_id=<id>`

- **Devices**:  
  - `POST /devices`  
  - `GET /devices`  
  - `PUT /devices/{id}/turn_on`  
  - `PUT /devices/{id}/turn_off`

### Pub/Sub Endpoints
- **List topics**:  
  `GET /topics` → returns `["users","rooms","devices","houses", ...]`

- **Manual publish**:  
  `POST /publish/{topic}` with JSON body  
  → publishes `{...}` to that channel

- **Subscribe** (Server-Sent Events):  
  `GET /subscribe/{topic}`  
  → keeps HTTP connection open and streams updates as `data: { ... }`

## 7. Example Workflow

1. **Subscribe** from a client or terminal:
   ```bash
   curl -N http://localhost:8000/subscribe/devices
   ```
2. **Trigger an event**:
   ```bash
   curl -X POST http://localhost:8000/devices \
     -H "Content-Type: application/json" \
     -d '{"name":"Lamp","device_type":"light","room_id":1}'
   ```
3. **Receive streamed message** in the subscriber console:
   ```
data: {"action":"create","device":{"id":1,"name":"Lamp","device_type":"light","status":"off","room_id":1}}
```

## 8. Shutting Down

- **Stop Uvicorn**: `CTRL+C` in the terminal
- **Stop Redis** (Homebrew):
  ```bash
  brew services stop redis
  ```
- **Or Docker**: `docker stop redis && docker rm redis`

---

Now you have a fully decoupled smart-home API where any number of front‑ends or microservices can subscribe to live updates via Redis Pub/Sub. Enjoy building real‑time dashboards, notification systems, or integrations on top of this foundation! 

