# Trade Opportunities API

A FastAPI service that analyzes market data and provides trade opportunity
insights for specific sectors in India, powered by Google Gemini.

---

## Setup

### 1. Clone & install dependencies

```bash
cd trade-opportunities-api
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set:

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key ([get one free](https://aistudio.google.com/app/apikey)) |
| `SECRET_KEY` | Random string for JWT signing |
| `RATE_LIMIT_REQUESTS` | Max requests per window (default: 10) |
| `RATE_LIMIT_WINDOW_SECONDS` | Window size in seconds (default: 60) |

### 3. Run the server

```bash
uvicorn main:app --reload --port 8000
```

---

## API Usage

### Authenticate

```bash
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'
```

Response:
```json
{"access_token": "<jwt>", "token_type": "bearer"}
```

### Analyze a sector

```bash
curl http://localhost:8000/analyze/pharmaceuticals \
  -H "Authorization: Bearer <jwt>"
```

The `report` field in the response contains a full Markdown document.

#### Save report to file

```bash
curl -s http://localhost:8000/analyze/pharmaceuticals \
  -H "Authorization: Bearer <jwt>" \
  | python -c "import sys,json; print(json.load(sys.stdin)['report'])" \
  > pharmaceuticals_report.md
```

---

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/token` | No | Get JWT token |
| `GET` | `/analyze/{sector}` | Bearer JWT | Generate sector report |
| `GET` | `/health` | No | Health check |
| `GET` | `/docs` | No | Swagger UI |
| `GET` | `/redoc` | No | ReDoc UI |

---

## Demo Credentials

| Username | Password |
|---|---|
| `demo` | `demo123` |
| `analyst` | `analyst456` |

---

## Security Features

- JWT Bearer authentication (HS256)
- Per-session sliding-window rate limiting
- Input validation (regex + length check on sector name)
- CORS middleware
- Structured error responses

---

## Architecture

```
main.py           — FastAPI app, routes, middleware
auth.py           — JWT creation, session management
rate_limiter.py   — Sliding-window rate limiter (in-memory)
data_collector.py — DuckDuckGo search for market data
analyzer.py       — Google Gemini integration
models.py         — Pydantic request/response models
config.py         — Environment-based configuration
```

---

## Supported Sectors (examples)

pharmaceuticals, technology, agriculture, automotive, textiles, chemicals,
electronics, steel, gems, jewelry, energy, infrastructure, finance,
healthcare, education, retail, logistics, manufacturing, defence, telecom

Any other sector name is also accepted — Gemini will analyze it.
