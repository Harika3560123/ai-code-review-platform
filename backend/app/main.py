import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from database.connection import init_db, check_db_connection
from routes import auth, review, findings, dashboard, fix

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("code_review.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Attempt database schema creation
    logger.info("Initializing database schema on startup...")
    init_db()
    db_ok, msg = check_db_connection()
    logger.info(f"Database readiness: {msg}")
    yield
    # Shutdown
    logger.info("Application shutting down.")

app = FastAPI(
    title="AI-Powered Code Review and Error Detection Platform Using Explainable AI",
    description="A hybrid code review and vulnerability analysis system combining AST parsing, static analyzers (Bandit, Pylint, ESLint, Semgrep), and Large Language Models with Explainable AI reasoning.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for local development, production Vercel frontend, and preview deployments
cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if settings.FRONTEND_URL:
    for origin_url in settings.FRONTEND_URL.split(","):
        cleaned_url = origin_url.strip()
        if cleaned_url and cleaned_url not in cors_origins:
            cors_origins.append(cleaned_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https://.*\.(vercel\.app|trycloudflare\.com)",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

# Register route modules
app.include_router(auth.router)
app.include_router(review.router)
app.include_router(findings.router)
app.include_router(dashboard.router)
app.include_router(fix.router)

@app.get("/", tags=["Health"])
def root():
    """System metadata and API entrypoint."""
    db_connected, db_message = check_db_connection()
    return {
        "title": "AI-Powered Code Review and Error Detection Platform Using Explainable AI",
        "status": "online",
        "version": "1.0.0",
        "database_connected": db_connected,
        "database_status": db_message,
        "docs_url": "/docs"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Service health probe checking backend and database connectivity."""
    db_connected, db_message = check_db_connection()
    return {
        "status": "healthy" if db_connected else "degraded",
        "database": {
            "connected": db_connected,
            "message": db_message
        }
    }
