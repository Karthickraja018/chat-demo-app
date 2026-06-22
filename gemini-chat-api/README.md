# Gemini Chat API

A production-ready backend chat API built with **FastAPI** and **Google Gemini**.

---

## Project Structure

```
gemini-chat-api/
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
- A [Google AI Studio](https://aistudio.google.com/app/apikey) API key

### Steps

```bash
# 1. Clone / enter the project
cd gemini-chat-api

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and set your GOOGLE_API_KEY

# 5. Run the server
uvicorn app:app --reload --port 8000
```

Server starts at `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

---

## API Endpoints

### GET `/`
Health check.

**Response**
```json
{ "message": "Gemini Chat API Running" }
```

### POST `/chat`
Send a message to Gemini and receive a response.

**Request body**
```json
{ "message": "What is Generative AI?" }
```

**Response**
```json
{ "response": "Generative AI refers to..." }
```

---

## API Testing

### cURL

```bash
# Health check
curl http://localhost:8000/

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Generative AI?"}'
```

### PowerShell

```powershell
Invoke-RestMethod -Uri http://localhost:8000/chat `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"message": "What is Generative AI?"}'
```

### Swagger UI

Open `http://localhost:8000/docs` in your browser and use the interactive UI to test endpoints.

---

## Docker

```bash
# Build
docker build -t gemini-chat-api .

# Run
docker run -p 8000:8000 -e GOOGLE_API_KEY=your_key gemini-chat-api
```

---

## Azure Deployment

### Option A — Azure Container Apps (recommended)

```bash
# 1. Login
az login

# 2. Create resource group
az group create --name gemini-chat-rg --location eastus

# 3. Create Container Registry
az acr create --resource-group gemini-chat-rg \
  --name geminichatacr --sku Basic --admin-enabled true

# 4. Build and push image
az acr build --registry geminichatacr \
  --image gemini-chat-api:latest .

# 5. Create Container Apps environment
az containerapp env create \
  --name gemini-chat-env \
  --resource-group gemini-chat-rg \
  --location eastus

# 6. Deploy
az containerapp create \
  --name gemini-chat-app \
  --resource-group gemini-chat-rg \
  --environment gemini-chat-env \
  --image geminichatacr.azurecr.io/gemini-chat-api:latest \
  --registry-server geminichatacr.azurecr.io \
  --env-vars GOOGLE_API_KEY=secretref:google-api-key \
  --secrets google-api-key=your_google_api_key \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 5
```

Your API will be live at the FQDN shown in the output.

### Option B — Azure App Service

```bash
# 1. Create App Service plan
az appservice plan create \
  --name gemini-chat-plan \
  --resource-group gemini-chat-rg \
  --is-linux --sku B1

# 2. Create web app from container
az webapp create \
  --resource-group gemini-chat-rg \
  --plan gemini-chat-plan \
  --name gemini-chat-app \
  --deployment-container-image-name geminichatacr.azurecr.io/gemini-chat-api:latest

# 3. Set environment variable
az webapp config appsettings set \
  --resource-group gemini-chat-rg \
  --name gemini-chat-app \
  --settings GOOGLE_API_KEY=your_google_api_key
```
