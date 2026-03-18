from collections import deque
from datetime import datetime, timezone
import logging

from fastapi import HTTPException, status

from config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS

logger = logging.getLogger(__name__)

# Per-session sliding window: jti -> deque of request timestamps
_request_log: dict[str, deque] = {}


def check_rate_limit(session: dict) -> None:
    """
    Sliding window rate limiter.
    Raises HTTP 429 if the session exceeds RATE_LIMIT_REQUESTS
    within RATE_LIMIT_WINDOW_SECONDS.
    """
    jti = session["session_id"]
    now = datetime.now(timezone.utc).timestamp()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    if jti not in _request_log:
        _request_log[jti] = deque()

    log = _request_log[jti]

    # Evict timestamps outside the window
    while log and log[0] < window_start:
        log.popleft()

    if len(log) >= RATE_LIMIT_REQUESTS:
        retry_after = int(RATE_LIMIT_WINDOW_SECONDS - (now - log[0]))
        logger.warning(
            f"Rate limit exceeded for session {jti} "
            f"(user={session['username']})"
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Rate limit exceeded. "
                f"Max {RATE_LIMIT_REQUESTS} requests per "
                f"{RATE_LIMIT_WINDOW_SECONDS}s. "
                f"Retry after {retry_after}s."
            ),
            headers={"Retry-After": str(retry_after)},
        )

    log.append(now)
    session["requests_made"] += 1
    session["last_request"] = datetime.now(timezone.utc)
    logger.debug(
        f"Request {len(log)}/{RATE_LIMIT_REQUESTS} for session {jti}"
    )
