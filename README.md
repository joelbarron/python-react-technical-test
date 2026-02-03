# Python + React Technical Test

Monorepo with Django/DRF + Celery/Redis + Django Channels + React, plus an RPA Selenium script.

## Architecture notes
- **Flow**: Frontend and RPA call Django (HTTP); frontend also subscribes to Django (WS).
- **Data**: Django persists to SQLite and publishes WS events on status changes.
- **Async**: Django enqueues work to Celery; Celery uses Redis as broker/result backend.
- **Realtime**: Django uses Redis as Channels layer to fan out WS updates.
- **Summarize**: Requests go through Django, which either calls OpenAI or a deterministic mock.

## Technical decisions
- **Stack choice**: Django/DRF for APIs, Channels for WS, Celery + Redis for async processing, React for the UI.
- **Persistence**: SQLite stored in-repo for quick local inspection and a simple demo setup.
- **Idempotency strategy**: header/body key + request hash enforced via unique constraint to guarantee safe retries.
- **Async flow**: explicit status transition `created → pending → processed/failed` to show lifecycle clearly.
- **Realtime updates**: WS events on each status change for live UI and external listeners.
- **Summarization fallback**: deterministic mock unless `OPENAI_API_KEY` is provided to avoid accidental API usage.
- **Dockerized runtime**: all services run via `docker compose up --build` with minimal host setup.

Architecture diagram:
```
┌────────────┐      HTTP/WS       ┌──────────────┐
│  Frontend  │ ────────────────▶  │  Django ASGI │
└────────────┘                    │  (DRF + WS)  │
┌────────────┐      HTTP          └──────┬───────┘
│ RPA Script │ ────────────────▶         │
└────────────┘                            │ writes/reads
                                         ▼
                                   ┌──────────┐
                                   │ SQLite   │
                                   └──────────┘
                                         │
                                         │ enqueue jobs
                                         ▼
                                   ┌──────────┐
                                   │ Celery   │
                                   │ Worker   │
                                   └────┬─────┘
                                        │
                                        │ broker/result + WS layer
                                        ▼
                                   ┌──────────┐
                                   │  Redis   │
                                   └──────────┘
```

## Structure
- `backend/` Django project (ASGI + Channels, Celery worker)
- `frontend/` React app (Vite)
- `rpa/` Selenium script
- `docker-compose.yml` at repo root
- `.env.example` at repo root
- `postman_collection.json` at repo root

## Run
1) Create and edit env:
```bash
cp .env.example .env
```
Update `.env` only if needed. By default the summarize endpoint uses a deterministic mock; set `OPENAI_API_KEY` (and optionally `OPENAI_MODEL`) only if you want real OpenAI responses.

2) Start services:
```bash
docker compose up --build
```

Services:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Redis: localhost:6379

## API examples (curl)
```bash
# POST /transactions/create
curl -X POST http://localhost:8000/transactions/create \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: demo-123' \
  -d '{"type":"credit","amount":"12.50"}'

# POST /transactions/async-process
curl -X POST http://localhost:8000/transactions/async-process \
  -H 'Content-Type: application/json' \
  -d '{"transaction_id":"<uuid>"}'

# GET /transactions/
curl http://localhost:8000/transactions/

# POST /assistant/summarize
curl -X POST http://localhost:8000/assistant/summarize \
  -H 'Content-Type: application/json' \
  -d '{"text":"Some long text."}'
```

WebSocket updates:
```bash
wscat -c ws://localhost:8000/ws/transactions/
```
Payloads look like:
```json
{ "event": "transaction.updated", "data": { "id": "...", "type": "credit", "amount": "10.00", "status": "processed", "created_at": "...", "updated_at": "..." } }
```

## RPA (Selenium)
Run with docker:
```bash
docker compose run --rm rpa python wiki_summarize.py "JavaScript"
```
The script opens Wikipedia, extracts the first paragraph for the term, calls the backend summarize endpoint, and prints the summary.

## Tests
```bash
docker compose run --rm backend python manage.py test
```
