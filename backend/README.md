# Team Standup Logger — Backend

A production-ready Flask backend for asynchronous daily standup updates. Team members submit standups via REST API; managers get real-time feeds and productivity analytics.

---

## Features

- **Standup CRUD** — Submit and retrieve daily standup posts
- **File Attachments** — Secure upload of PNG, JPG, JPEG, PDF (max 5 MB)
- **Weather Enrichment** — Auto-fetches Nairobi weather (Open-Meteo, no API key) on every submission
- **Productivity Stats** — Posts per day, blocker counts, active users (last 7 days)
- **Real-time Feed** — Socket.IO `/feed` namespace emits `new_standup` events instantly
- **Polling-Friendly** — GET `/api/standups` works for React's 10-second poll fallback
- **Centralized Error Handling** — All errors return consistent JSON envelopes
- **Database Migrations** — Flask-Migrate / Alembic
- **17 passing tests** — Covers health, CRUD, validation, file uploads, stats, pagination

---

## Tech Stack

| Layer        | Library              |
|-------------|----------------------|
| Framework   | Flask 3              |
| ORM         | Flask-SQLAlchemy     |
| Migrations  | Flask-Migrate        |
| Validation  | Marshmallow          |
| Real-time   | Flask-SocketIO       |
| CORS        | Flask-CORS           |
| File upload | Werkzeug             |
| Weather     | Open-Meteo REST API  |
| Server      | Gunicorn + Eventlet  |

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Application factory (create_app)
│   ├── config/
│   │   └── settings.py      # Dev / Prod / Test config classes
│   ├── extensions/
│   │   └── __init__.py      # db, migrate, cors, socketio instances
│   ├── models/
│   │   └── standup.py       # StandupPost SQLAlchemy model
│   ├── schemas/
│   │   └── standup_schema.py# Marshmallow input/output schemas
│   ├── routes/
│   │   ├── standups.py      # POST/GET /api/standups, GET /api/standups/stats
│   │   └── health.py        # GET /api/health, GET /api/uploads/<file>
│   ├── services/
│   │   ├── standup_service.py  # Business logic (create, list, stats)
│   │   └── weather_service.py  # Open-Meteo integration
│   ├── sockets/
│   │   └── feed.py          # Socket.IO /feed namespace handlers
│   └── utils/
│       ├── file_upload.py   # Secure file save/delete helpers
│       ├── responses.py     # success_response / error_response
│       └── error_handlers.py# Centralized JSON error handlers
├── migrations/              # Alembic migration scripts
├── uploads/                 # Uploaded files (git-ignored)
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   └── test_api.py          # 17 API tests
├── seed.py                  # Sample data seeder
├── run.py                   # Dev server entry point
├── Procfile                 # Render / Railway deployment
├── Dockerfile               # Container build
├── requirements.txt
└── .env                     # Environment variables (git-ignored)
```

---

## Installation

### 1. Clone & enter

```bash
git clone <repo-url>
cd backend
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Copy `.env` and edit as needed:

```bash
cp .env .env.local
```

Required variables:

```env
FLASK_ENV=development
SECRET_KEY=your-random-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///standup_logger.db
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
MAX_CONTENT_LENGTH=5242880
UPLOAD_FOLDER=uploads
OPEN_METEO_LAT=1.2921
OPEN_METEO_LON=36.8219
```

---

## Database Setup

```bash
# Initialise migration repository (first time only)
flask db init

# Generate migration from models
flask db migrate -m "initial standup_posts table"

# Apply to database
flask db upgrade

# (Optional) Seed with sample data
python seed.py
```

---

## Running the Server

### Development

```bash
python run.py
```

Server starts at `http://localhost:5000`

### Production (Gunicorn + Eventlet)

```bash
gunicorn -k eventlet -w 1 --bind 0.0.0.0:5000 run:app
```

> **Important:** Use exactly 1 worker (`-w 1`) with `eventlet`. Multiple workers require a Redis message queue for Socket.IO.

---

## Deploying Publicly

This repository can be deployed as a single Docker service that serves both the Flask API and the built frontend static app.

### Render Deploy

A Render manifest is included at the repository root: `render.yaml`.

To deploy:

1. Push the repo to GitHub or GitLab.
2. In Render, create a new service and connect your repo.
3. Render will use the Dockerfile at `backend/Dockerfile`.

The manifest config uses:

- `type: web_service`
- `env: docker`
- `dockerfilePath: backend/Dockerfile`
- `healthCheckPath: /api/health`
- `FLASK_ENV=production`
- `PORT=5000`
- `DATABASE_URL=sqlite:///standup_logger.db`
- `CORS_ORIGINS=https://final-standup-logger.onrender.com`

> Note: SQLite is fine for a simple demo, but for persistent production data you should attach a managed database and set `DATABASE_URL` to the provided Render Postgres URL.

### Local Docker

1. Build from the repository root:

```bash
docker build -f backend/Dockerfile -t standup-app .
```

2. Run the container:

```bash
docker run -p 5000:5000 standup-app
```

3. Open the app in your browser:

```text
http://localhost:5000
```

---

## API Reference

### Health

```
GET /api/health
```

**Response:**
```json
{
  "success": true,
  "message": "Service is up",
  "data": { "status": "healthy" }
}
```

---

### Submit Standup

```
POST /api/standups
Content-Type: multipart/form-data
```

**Fields:**

| Field      | Type   | Required | Description                    |
|-----------|--------|----------|-------------------------------|
| author    | string | ✅       | Team member name               |
| yesterday | string | ✅       | What they worked on yesterday  |
| today     | string | ✅       | What they're doing today       |
| blockers  | string | ❌       | Any blockers (leave empty if none) |
| attachment| file   | ❌       | PNG, JPG, JPEG, or PDF (≤5 MB) |

**Response (201):**
```json
{
  "success": true,
  "message": "Standup submitted!",
  "data": {
    "id": 1,
    "author": "Alice Mwangi",
    "yesterday": "Wrote unit tests for auth module.",
    "today": "Building the dashboard charts.",
    "blockers": "",
    "has_blocker": false,
    "attachment_url": null,
    "weather_condition": "Partly cloudy",
    "temperature": 22.3,
    "created_at": "2026-06-04T08:00:00+00:00"
  }
}
```

**Validation error (422):**
```json
{
  "success": false,
  "message": "Validation failed",
  "data": null,
  "errors": { "author": ["Missing data for required field."] }
}
```

---

### List Standups

```
GET /api/standups?limit=50&offset=0
```

Returns all standups ordered newest-first. Supports pagination.

---

### Productivity Stats

```
GET /api/standups/stats
```

**Response:**
```json
{
  "success": true,
  "message": "OK",
  "data": {
    "total_posts": 42,
    "active_users_count": 5,
    "blocker_count": 7,
    "posts_per_day": [
      { "date": "2026-05-29", "count": 4 },
      { "date": "2026-05-30", "count": 6 }
    ],
    "blocker_per_day": [
      { "date": "2026-05-29", "count": 1 },
      { "date": "2026-05-30", "count": 2 }
    ]
  }
}
```

---

### Serve Upload

```
GET /api/uploads/<filename>
```

Returns the uploaded file. Uses `send_from_directory` to prevent path traversal.

---

## File Upload

- Allowed types: `png`, `jpg`, `jpeg`, `pdf`
- Max size: 5 MB (configurable via `MAX_CONTENT_LENGTH`)
- Filenames are replaced with UUID hex strings (e.g. `a3f9c2...jpg`) to prevent enumeration
- Files stored in the `uploads/` directory

**curl example:**
```bash
curl -X POST http://localhost:5000/api/standups \
  -F "author=Alice" \
  -F "yesterday=Fixed the upload bug" \
  -F "today=Writing tests" \
  -F "blockers=" \
  -F "attachment=@/path/to/screenshot.png"
```

---

## Socket.IO

**Namespace:** `/feed`

### Server → Client Events

| Event          | Payload                  | Description                    |
|---------------|--------------------------|-------------------------------|
| `connected`    | `{message: string}`      | Fired on connect               |
| `new_standup`  | StandupPost object       | Fired when a standup is posted |
| `feed_snapshot`| StandupPost[]            | Latest 10 on `request_feed`   |

### Client → Server Events

| Event          | Description                                      |
|---------------|--------------------------------------------------|
| `request_feed` | Ask for a snapshot of the 10 most recent posts  |

**JavaScript example:**
```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:5000/feed');

socket.on('connect', () => {
  socket.emit('request_feed');
});

socket.on('feed_snapshot', (posts) => {
  console.log('Initial posts:', posts);
});

socket.on('new_standup', (post) => {
  console.log('New standup:', post);
});
```

---

## Running Tests

```bash
FLASK_ENV=testing pytest tests/ -v
```

All 17 tests should pass.

---

## Deployment

### Render / Railway

1. Set environment variables in the dashboard (copy from `.env`)
2. Build command: `pip install -r requirements.txt && flask db upgrade`
3. Start command: `gunicorn -k eventlet -w 1 run:app`

The `Procfile` is pre-configured.

### Docker

```bash
docker build -t standup-logger .
docker run -p 5000:5000 \
  -e SECRET_KEY=prod-secret \
  -e DATABASE_URL=sqlite:///standup_logger.db \
  standup-logger
```

### VPS (systemd)

```ini
# /etc/systemd/system/standup.service
[Unit]
Description=Team Standup Logger
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/standup-logger/backend
ExecStart=/opt/standup-logger/venv/bin/gunicorn -k eventlet -w 1 --bind 0.0.0.0:5000 run:app
Restart=always
EnvironmentFile=/opt/standup-logger/backend/.env

[Install]
WantedBy=multi-user.target
```

---

## Frontend Integration Notes

The API is optimized for a React frontend that:

- **Polls** `GET /api/standups` every 10 seconds
- **Uploads** files via `multipart/form-data`
- **Renders** weather badge from `temperature` + `weather_condition`
- **Charts** `posts_per_day` and `blocker_per_day` arrays (ready for Recharts/Chart.js)
- **Subscribes** to Socket.IO `/feed` for instant updates without polling

All responses use a consistent `{ success, message, data }` envelope.
