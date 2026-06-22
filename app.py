import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langsmith import traceable

load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Environment validation
# ---------------------------------------------------------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY environment variable is not set")

# LangSmith reads LANGSMITH_API_KEY and LANGSMITH_TRACING automatically.
# Set LANGSMITH_PROJECT to group traces under a named project.

# ---------------------------------------------------------------------------
# LangChain / Gemini model
# ---------------------------------------------------------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=GOOGLE_API_KEY,
)

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Schemas  (unchanged)
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="User message")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Gemini model response")


class HealthResponse(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# Traced model invocation
# ---------------------------------------------------------------------------
@traceable(name="gemini_invoke", run_type="llm")
def invoke_gemini(message: str) -> str:
    """Call the Gemini model via LangChain and return the text reply."""
    result = llm.invoke([HumanMessage(content=message)])
    return result.content


# ---------------------------------------------------------------------------
# Endpoints  (routes / schemas unchanged)
# ---------------------------------------------------------------------------
@app.get("/", response_model=HealthResponse, summary="Health check")
async def root():
    return {"message": "Gemini Chat API Running"}


@app.post("/chat", response_model=ChatResponse, summary="Send a message to Gemini")
@traceable(name="chat_endpoint", run_type="chain")
async def chat(request: ChatRequest):
    logger.info("Request received: %s", request.message[:120])
    try:
        logger.info("Invoking Gemini model")
        response_text = invoke_gemini(request.message)
        logger.info("Success response generated")
        return {"response": response_text}
    except Exception as e:
        logger.error("Gemini API error: %s", str(e))
        raise HTTPException(status_code=500, detail={"error": str(e)})
