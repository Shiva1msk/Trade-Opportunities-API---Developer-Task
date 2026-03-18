import logging
import uuid
import warnings
from datetime import datetime, timedelta, timezone
from typing import Optional

# Suppress passlib/bcrypt version detection noise (cosmetic only, no impact)
warnings.filterwarnings("ignore", ".*bcrypt.*")
logging.getLogger("passlib").setLevel(logging.ERROR)

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

# In-memory user store (demo users)
USERS_DB: dict[str, dict] = {
    "demo": {
        "username": "demo",
        "hashed_password": pwd_context.hash("demo123"),
    },
    "analyst": {
        "username": "analyst",
        "hashed_password": pwd_context.hash("analyst456"),
    },
}

# Active sessions: token_jti -> session metadata
SESSIONS: dict[str, dict] = {}


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = USERS_DB.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(username: str) -> str:
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,
        "jti": jti,
        "exp": expire,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    # Register session
    SESSIONS[jti] = {
        "session_id": jti,
        "username": username,
        "requests_made": 0,
        "last_request": None,
        "created_at": datetime.now(timezone.utc),
    }
    logger.info(f"Session created for user '{username}' (jti={jti})")
    return token


def get_current_session(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        jti: str = payload.get("jti")
        if not username or not jti:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    session = SESSIONS.get(jti)
    if not session:
        raise credentials_exception

    return session
