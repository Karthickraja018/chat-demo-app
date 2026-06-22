# Gemini Chat API

A production-ready backend chat API built with **FastAPI**, **Google Gemini**, and **LangSmith** observability.

---

## What changed (LangSmith integration)

| Area | Before | After |
|---|---|---|
| Gemini SDK | `google-generativeai` direct calls | `langchain-google-genai` via LangChain |
| Observability | None | LangSmith traces every request & LLM call |
| Logging | None | Structured `logging` module |
| Error body | Plain string | `{"error": "message"}` JSON |
| Model init | `genai.GenerativeModel(...)` | `ChatGoogleGenerativeAI(...)` |

---

## Project Structure

```
deploy/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
└── README.md
```

---

## Local Setup

### Prerequisites
- Python 3.12+
- [Google AI Studio](https://aistudio.google.com/app/apikey) API key
- [LangSmith](https://smith.langchain.com) account + API key

### Steps

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — set GOOGLE_API_KEY and LANGSMITH_API_KEY

# 4. Run the server
uvicorn app:app --reload --port 8000
```

Server: `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | Yes | Google Gemini API key |
| `LANGSMITH_API_KEY` | Yes | LangSmith API key |
| `LANGSMITH_TRACING` | Yes | Set to `true` to enable tracing |
| `LANGSMITH_PROJECT` | No | Project name in LangSmith (default: `default`) |

---

## API Endpoints

### GET `/`

Health check.

```json
{ "message": "Gemini Chat API Running" }
```

### POST `/chat`

Send a message to Gemini.

**Request**
```json
{ "message": "What is Generative AI?" }
```

**Response**
```json
{ "response": "Generative AI refers to..." }
```

**Error**
```json
{ "detail": { "error": "description of the error" } }
```

---

## API Testing

```bash
# Health check
curl http://localhost:8000/

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Generative AI?"}'
```

---

## Docker

```bash
docker build -t gemini-chat-api .

docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=your_key \
  -e LANGSMITH_API_KEY=your_key \
  -e LANGSMITH_TRACING=true \
  -e LANGSMITH_PROJECT=Gemini-Chat-App \
  gemini-chat-api
```

---

## Azure App Service Deployment

### Required Azure Environment Variables

Set these in **Azure Portal → App Service → Settings → Environment variables** (or via CLI):

| Variable | Value |
|---|---|
| `GOOGLE_API_KEY` | Your Google Gemini API key |
| `LANGSMITH_API_KEY` | Your LangSmith API key |
| `LANGSMITH_TRACING` | `true` |
| `LANGSMITH_PROJECT` | `Gemini-Chat-App` |

#### Set via Azure CLI

```bash
az webapp config appsettings set \
  --resource-group <your-resource-group> \
  --name chat-demo-webapp \
  --settings \
    GOOGLE_API_KEY="your_google_api_key" \
    LANGSMITH_API_KEY="your_langsmith_api_key" \
    LANGSMITH_TRACING="true" \
    LANGSMITH_PROJECT="Gemini-Chat-App"
```

---

### GitHub Secrets

Add these secrets in **GitHub → Repository → Settings → Secrets and variables → Actions**:

| Secret | Description |
|---|---|
| `AZUREAPPSERVICE_PUBLISHPROFILE_...` | Azure publish profile (already set by Azure portal) |

The LangSmith and Google keys are set directly on the Azure App Service — they do **not** need to be GitHub secrets unless you want to inject them at build time.

---

### Deployment Steps

CI/CD is handled by `.github/workflows/main_chat-demo-webapp.yml`.

1. Push to `main` branch — GitHub Actions triggers automatically.
2. The workflow installs dependencies, uploads the artifact, and deploys to Azure App Service `chat-demo-webapp`.
3. Azure Oryx builds the app on the platform using `requirements.txt`.

Manual deploy trigger:

```
GitHub → Actions → "Build and deploy Python app" → Run workflow
```

---

### Validation Steps

After deployment:

```bash
# 1. Health check
curl https://chat-demo-webapp.azurewebsites.net/

# Expected: {"message":"Gemini Chat API Running"}

# 2. Chat endpoint
curl -X POST https://chat-demo-webapp.azurewebsites.net/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Expected: {"response":"..."}

# 3. LangSmith — open https://smith.langchain.com
#    Navigate to project "Gemini-Chat-App"
#    You should see a trace for each /chat request with:
#      - chat_endpoint (chain run)
#      - gemini_invoke  (llm run) with input/output and latency
```

---

## LangSmith Trace Structure

Each `/chat` call produces a two-level trace:

```
chat_endpoint  [chain]
└── gemini_invoke  [llm]
      input:  { message }
      output: { content }
      latency, tokens, errors
```

Errors are captured automatically and surfaced in the LangSmith UI with full stack traces.
