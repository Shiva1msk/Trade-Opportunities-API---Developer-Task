# 🚀 Trade Opportunities API

A **production-ready FastAPI service** that analyzes market data and generates **AI-powered trade opportunity insights** for various sectors in India using Google Gemini.

---

## ✨ Features

* 🔐 JWT-based authentication (HS256)
* 🤖 AI-powered analysis using Google Gemini
* 🌐 Real-time market data collection (DuckDuckGo)
* 🚦 Sliding-window rate limiting
* ✅ Input validation with Pydantic
* 🔄 CORS middleware support
* 📄 Structured Markdown reports
* ⚡ High-performance FastAPI backend
* ☁️ Deployed on Render

---

## 🧠 How It Works

1. User authenticates and receives a JWT token
2. User sends a sector name (e.g., `technology`)
3. System collects relevant market data
4. Gemini AI analyzes the data
5. API returns a structured trade opportunity report

---

## ⚙️ Setup

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/Shiva1msk/Trade-Opportunities-API---Developer-Task.git
cd trade-opportunities-api
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

| Variable                    | Description                           |
| --------------------------- | ------------------------------------- |
| `GEMINI_API_KEY`            | Your Google Gemini API key            |
| `SECRET_KEY`                | Secret key for JWT signing            |
| `RATE_LIMIT_REQUESTS`       | Max requests per window (default: 10) |
| `RATE_LIMIT_WINDOW_SECONDS` | Window size in seconds (default: 60)  |

---

### 3. Run the Server

```bash
uvicorn main:app --reload --port 8000
```

---

## 🔑 API Usage

### 🔐 Authenticate

```bash
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'
```

**Response:**

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

---

### 📊 Analyze a Sector

```bash
curl http://localhost:8000/analyze/pharmaceuticals \
  -H "Authorization: Bearer <jwt>"
```

👉 The response contains a `report` field with a full Markdown analysis.

---

### 💾 Save Report to File

```bash
curl -s http://localhost:8000/analyze/pharmaceuticals \
  -H "Authorization: Bearer <jwt>" \
  | python -c "import sys,json; print(json.load(sys.stdin)['report'])" \
  > pharmaceuticals_report.md
```

---

## 📡 API Endpoints

| Method | Path                | Auth  | Description            |
| ------ | ------------------- | ----- | ---------------------- |
| `POST` | `/token`            | ❌ No  | Generate JWT token     |
| `GET`  | `/analyze/{sector}` | ✅ Yes | Generate sector report |
| `GET`  | `/health`           | ❌ No  | Health check           |
| `GET`  | `/docs`             | ❌ No  | Swagger UI             |
| `GET`  | `/redoc`            | ❌ No  | ReDoc UI               |

---

## 👤 Demo Credentials

| Username  | Password     |
| --------- | ------------ |
| `demo`    | `demo123`    |
| `analyst` | `analyst456` |

---

## 🔐 Security Features

* JWT Bearer authentication (HS256)
* Sliding-window rate limiting
* Input validation (regex + length checks)
* CORS middleware
* Structured error handling

---

## 🏗️ Architecture

```
main.py           — FastAPI app, routes, middleware
auth.py           — JWT authentication & session management
rate_limiter.py   — Sliding-window rate limiter
data_collector.py — Market data collection (DuckDuckGo)
analyzer.py       — Google Gemini integration
models.py         — Pydantic schemas
config.py         — Environment configuration
```

---

## 🌍 Supported Sectors

Examples:

```
pharmaceuticals, technology, agriculture, automotive, textiles,
chemicals, electronics, steel, finance, healthcare, education,
retail, logistics, defence, telecom
```

👉 Any custom sector is also supported.

---

## 🚀 Deployment

Live API Docs:
👉 https://trade-opportunities-api-developer-task-klll.onrender.com/docs#/

---

## 💡 Future Improvements

* Database integration (PostgreSQL)
* Redis caching for performance
* User registration system
* Store historical reports
* Async background processing
* Frontend dashboard

---

## 👨‍💻 Author

**Maidam Shiva Kumar**

---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub!
