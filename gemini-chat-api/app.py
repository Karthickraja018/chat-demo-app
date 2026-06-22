import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY environment variable is not set")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-3.1-flash-lite")

app = FastAPI(
    title="Gemini Chat API",
    description="A production-ready chat API powered by Google Gemini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="User message")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Gemini model response")


class HealthResponse(BaseModel):
    message: str


@app.get("/", response_model=HealthResponse, summary="Health check")
async def root():
    return {"message": "Gemini Chat API Running"}


@app.post("/chat", response_model=ChatResponse, summary="Send a message to Gemini")
async def chat(request: ChatRequest):
    try:
        result = model.generate_content(request.message)
        return {"response": result.text}
    except genai.types.BlockedPromptException as e:
        raise HTTPException(status_code=400, detail=f"Prompt was blocked: {e}")
    except genai.types.StopCandidateException as e:
        raise HTTPException(status_code=400, detail=f"Generation stopped unexpectedly: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
