import logging
import re
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from auth import authenticate_user, create_access_token, get_current_session
from analyzer import generate_analysis
from data_collector import collect_sector_data
from models import AnalysisResponse, ErrorResponse, Token, TokenRequest
from rate_limiter import check_rate_limit
from config import VALID_SECTORS

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Trade Opportunities API",
    description=(
        "Analyzes market data and provides trade opportunity insights "
        "for specific sectors in India."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"},
    )


# ---------------------------------------------------------------------------
# Auth endpoint
# ---------------------------------------------------------------------------

@app.post(
    "/token",
    response_model=Token,
    summary="Obtain a JWT access token",
    tags=["Authentication"],
)
async def login(body: TokenRequest):
    """
    Authenticate with username/password and receive a Bearer token.

    **Demo credentials:**
    - `demo` / `demo123`
    - `analyst` / `analyst456`
    """
    user = authenticate_user(body.username, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token(user["username"])
    logger.info(f"Token issued for user '{user['username']}'")
    return Token(access_token=token, token_type="bearer")


# ---------------------------------------------------------------------------
# Core endpoint
# ---------------------------------------------------------------------------

@app.get(
    "/analyze/{sector}",
    response_model=AnalysisResponse,
    summary="Get trade opportunity analysis for an Indian sector",
    tags=["Analysis"],
    responses={
        200: {"description": "Markdown analysis report"},
        400: {"model": ErrorResponse, "description": "Invalid sector name"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def analyze_sector(
    sector: str,
    session: dict = Depends(get_current_session),
):
    """
    Returns a structured Markdown trade opportunity report for the given
    **sector** in India.

    - Searches for current market data via DuckDuckGo
    - Analyzes collected data using Google Gemini
    - Applies per-session rate limiting

    **Supported sectors (examples):** pharmaceuticals, technology, agriculture,
    automotive, textiles, chemicals, electronics, steel, energy, and more.
    """
    # --- Input validation ---
    sector_clean = sector.strip().lower()

    if not re.match(r"^[a-z][a-z\s\-]{1,49}$", sector_clean):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sector name must be 2-50 alphabetic characters.",
        )

    # Warn but don't block unknown sectors — Gemini can still analyze them
    if sector_clean not in VALID_SECTORS:
        logger.info(
            f"Sector '{sector_clean}' not in predefined list — proceeding anyway."
        )

    # --- Rate limiting ---
    check_rate_limit(session)

    # --- Data collection ---
    logger.info(
        f"Analyzing sector='{sector_clean}' for user='{session['username']}'"
    )
    try:
        collected = await collect_sector_data(sector_clean)
    except Exception as e:
        logger.error(f"Data collection failed: {e}")
        collected = {"sector": sector_clean, "queries": [], "results": []}

    # --- AI analysis ---
    try:
        report = await generate_analysis(sector_clean, collected)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )

    return AnalysisResponse(
        sector=sector_clean,
        generated_at=datetime.now(timezone.utc),
        report=report,
    )


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["System"], summary="Health check")
async def health():
    return {"status": "ok", "service": "trade-opportunities-api"}
